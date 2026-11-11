from pathlib import Path
import json
import tempfile
import asyncio
import logging
import os
import re
import subprocess
import zipfile
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from backend.config import (
    EXPORTS_DIR,
    TEMP_DIR,
    download_clip_segment,
    generate_ass_file,
    has_emoji,
    is_valid_mp4,
    logger,
    render_clip_to_mp4,
    render_title_overlay_png,
    transcribe_clip_words,
)
from backend.schemas.render import RenderBatchRequest, RenderSettingsModel
from backend.utils.text import is_twitch_url, extract_twitch_info, get_twitch_canonical_url, canonical_video_url

RENDER_BATCHES: Dict[str, Dict[str, Any]] = {}
BATCH_REQUESTS: Dict[str, RenderBatchRequest] = {}
# Concurrency gate: serialize video rendering (1 active render job at a time) to prevent CPU starvation on low-spec servers
_RENDER_SEMAPHORE = asyncio.Semaphore(1)


def add_render_log(batch_id: str, message: str, level: str = "info", clip_index: Optional[int] = None):
    """Append a bounded, timestamped real backend event to a render batch."""
    batch = RENDER_BATCHES.get(batch_id)
    if not batch:
        return

    logs = batch.setdefault("logs", [])
    logs.append({
        "timestamp": datetime.now().astimezone().isoformat(timespec="seconds"),
        "message": str(message)[:500],
        "level": level if level in ("info", "progress", "success", "error", "warning") else "info",
        "clip_index": clip_index
    })

    if len(logs) > 300:
        del logs[:-300]


def _ensure_concat_streams(file_path: str) -> bool:
    """Ensure a segment has video and audio before merged concat."""
    probe_cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "stream=codec_type",
        "-of", "csv=p=0",
        file_path,
    ]
    probe = subprocess.run(
        probe_cmd, capture_output=True, text=True, timeout=15
    )

    file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
    logger.info(
        f"SEGMENT DIAGNOSTIC | file={Path(file_path).name} "
        f"| size={file_size} | ffprobe_rc={probe.returncode} "
        f"| streams={probe.stdout.strip()!r} "
        f"| stderr={probe.stderr[-1000:]!r}"
    )

    if probe.returncode != 0:
        raise RuntimeError(
            f"ffprobe gagal memeriksa segmen: {probe.stderr[-1500:]}"
        )

    stream_types = {
        line.strip() for line in probe.stdout.splitlines() if line.strip()
    }

    if "video" not in stream_types:
        raise RuntimeError(
            f"Segmen tidak memiliki video stream: {Path(file_path).name}"
        )

    if "audio" in stream_types:
        return False

    temp_path = str(Path(file_path).with_name(
        Path(file_path).stem + "_audiofix.mp4"
    ))

    try:
        cmd = [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-i", file_path,
            "-f", "lavfi", "-i",
            "anullsrc=channel_layout=stereo:sample_rate=48000",
            "-map", "0:v:0", "-map", "1:a:0",
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "192k",
            "-shortest",
            "-movflags", "+faststart",
            temp_path,
        ]

        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=180
        )

        if result.returncode != 0:
            raise RuntimeError(
                f"Gagal menambahkan silent audio: {result.stderr[-2000:]}"
            )

        if not is_valid_mp4(temp_path):
            raise RuntimeError("Hasil perbaikan audio tidak valid.")

        os.replace(temp_path, file_path)
        logger.info(
            f"Silent audio ditambahkan ke segmen {Path(file_path).name}"
        )
        return True

    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)



def _probe_media_duration(file_path: str) -> float:
    """Return the actual probed media duration (prefer container, then video stream)."""
    command = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration:stream=codec_type,duration",
        "-of", "json", file_path,
    ]
    result = subprocess.run(
        command, capture_output=True, text=True, timeout=20, check=False
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"ffprobe gagal membaca durasi {Path(file_path).name}: "
            f"{(result.stderr or '')[-1200:]}"
        )
    try:
        payload = json.loads(result.stdout or "{}")
        raw_duration = payload.get("format", {}).get("duration")
        duration = float(raw_duration) if raw_duration not in (None, "", "N/A") else 0.0
        if duration <= 0:
            video_durations = [
                float(stream["duration"])
                for stream in payload.get("streams", [])
                if stream.get("codec_type") == "video"
                and stream.get("duration") not in (None, "", "N/A")
                and float(stream["duration"]) > 0
            ]
            duration = max(video_durations) if video_durations else 0.0
    except (TypeError, ValueError, KeyError, json.JSONDecodeError) as exc:
        raise RuntimeError(
            f"Metadata durasi tidak valid untuk {Path(file_path).name}: {exc}"
        ) from exc
    if not (0.05 < duration < 86400):
        raise RuntimeError(
            f"Durasi media tidak valid untuk {Path(file_path).name}: {duration!r}"
        )
    return duration



async def render_single_batch_clip(
    batch_id: str,
    idx: int,
    clip: Dict[str, Any],
    settings: RenderSettingsModel,
    target_url: str,
    transcript: Optional[List[Dict[str, Any]]] = None,
    total_clips: int = 1,
    cookies_content: Optional[str] = None
):
    batch = RENDER_BATCHES.get(batch_id)
    if not batch:
        return

    clip_status = batch["clips"][idx]
    clip_status["status"] = "downloading"
    clip_status["progress_percent"] = 15
    add_render_log(batch_id, f"Clip {idx + 1}: mulai mengunduh sumber video", clip_index=idx)
    clip_status["error_message"] = None
    clip_status["error"] = None

    raw_path = None
    ass_path = None
    title_overlay_path = None

    try:
        # 1. Download
        start_t = float(clip.get("start_time", 0.0))
        end_t = float(clip.get("end_time", start_t + 30.0))
        seg_filename = f"{batch_id}_clip_{idx}_raw.mp4"

        def _on_download_progress(info: Dict[str, Any]):
            percent = max(0.0, min(100.0, float(info.get("percent", 0) or 0)))
            clip_status["download_percent"] = percent
            clip_status["downloaded"] = info.get("downloaded", "")
            clip_status["download_total"] = info.get("total", "")
            clip_status["download_speed"] = info.get("speed", "")
            clip_status["download_eta"] = info.get("eta", "")
            clip_status["download_phase"] = info.get("phase", "download")
            clip_status["progress_percent"] = 15 + int(percent * 0.25)

        raw_path = await asyncio.to_thread(
            download_clip_segment,
            target_url,
            start_t,
            end_t,
            seg_filename,
            cookies_content,
            _on_download_progress
        )

        if not raw_path or not os.path.exists(raw_path) or not is_valid_mp4(raw_path):
            raise RuntimeError(
                "Source video segment is incomplete or corrupted ('moov atom not found'). "
                "Network lag interrupted the download. Please retry rendering this clip."
            )

        # 2. Transcribe & Generate Subtitles / Title (.ass)
        clip_status["status"] = "transcribing"
        clip_status["progress_percent"] = 40
        add_render_log(batch_id, f"Clip {idx + 1}: mulai transkripsi audio dan pembuatan subtitle", clip_index=idx)

        display_title = None
        base_title = (
            clip.get("custom_title")
            or clip.get("title_suggestion")
            or clip.get("title")
            or f"Clip {idx+1}"
        ).strip()

        if settings.title_position != "none":
            pfx = settings.title_prefix or ""
            sfx = settings.title_suffix or ""
            if pfx or sfx:
                display_title = f"{pfx}{base_title}{sfx}".strip()
            elif total_clips == 1 and settings.title_text and settings.title_text.strip() and not (clip.get("custom_title") or clip.get("title_suggestion")):
                display_title = settings.title_text.strip()
            else:
                display_title = base_title

        clip_status["title"] = display_title or base_title
        clip_status["base_title"] = base_title

        skip_ass_title = False
        duration_sec = max(1.0, end_t - start_t)

        # Check if title has emoji -> render transparent color emoji PNG overlay
        if display_title and settings.title_position != "none" and has_emoji(display_title):
            title_png_filename = f"{batch_id}_clip_{idx}_title.png"
            title_png_path = str(TEMP_DIR / title_png_filename)
            try:
                canvas_w = 1920 if (settings.aspect_ratio == "16:9_landscape") else 1080
                canvas_h = 1080 if (settings.aspect_ratio == "16:9_landscape") else 1920
                rendered_overlay = await asyncio.to_thread(
                    render_title_overlay_png,
                    title_text=display_title,
                    output_png_path=title_png_path,
                    font_name=settings.title_font or settings.caption_font or "Outfit",
                    target_aspect_ratio=settings.aspect_ratio or "9:16",
                    font_size_preset=settings.title_font_size or settings.font_size or "medium",
                    text_case=settings.title_text_case or settings.text_case or "uppercase",
                    title_position=settings.title_position or "auto",
                    title_y_percent=settings.title_y_percent,
                    canvas_w=canvas_w,
                    canvas_h=canvas_h,
                    title_font_size_preset=settings.title_font_size or settings.font_size or "medium",
                    streamer_preset=settings.streamer_preset or "none",
                    title_font_name=settings.title_font or settings.caption_font or "Outfit",
                    title_font_size_px=settings.title_font_size_px,
                    title_text_case=settings.title_text_case or settings.text_case or "uppercase",
                    title_x_percent=getattr(settings, "title_x_percent", 50.0)
                )
                if rendered_overlay and os.path.exists(rendered_overlay):
                    title_overlay_path = rendered_overlay
                    skip_ass_title = True
                    logger.info(f"Rendered full-color emoji title overlay: {title_overlay_path}")
            except Exception as ex:
                logger.warning(f"Could not render color emoji title overlay: {ex}")
                skip_ass_title = False

        # Detect language from transcript or video context
        target_lang = None
        if transcript:
            try:
                from backend.utils.text import detect_transcript_language
                detected = detect_transcript_language(transcript[:50], display_title or "")
                if detected and detected.get("code") in ("id", "en"):
                    target_lang = detected["code"]
            except Exception:
                pass

        if settings.caption_style != "none" or (display_title and settings.title_position != "none" and not skip_ass_title):
            words = []
            if settings.caption_style != "none":
                words = await asyncio.to_thread(
                    transcribe_clip_words,
                    raw_path,
                    transcript,
                    start_t,
                    end_t,
                    target_lang
                )
            ass_filename = f"{batch_id}_clip_{idx}.ass"
            ass_path = str(TEMP_DIR / ass_filename)
            await asyncio.to_thread(
                generate_ass_file,
                words=words,
                style_preset=settings.caption_style,
                font_name=settings.caption_font or "Outfit",
                output_ass_path=ass_path,
                target_aspect_ratio=settings.aspect_ratio,
                font_size_preset=settings.font_size,
                text_case=settings.text_case,
                title_text=display_title if not skip_ass_title else None,
                title_position=settings.title_position,
                title_duration=settings.title_duration if settings.title_duration else "entire",
                duration_seconds=duration_sec,
                title_y_percent=settings.title_y_percent,
                subtitle_y_percent=settings.subtitle_y_percent,
                subtitle_position_mode=settings.subtitle_position_mode if settings.subtitle_position_mode else "bottom",
                subtitle_center_y_percent=settings.subtitle_center_y_percent if settings.subtitle_center_y_percent is not None else 50.0,
                skip_title=skip_ass_title,
                title_font_size_preset=settings.title_font_size or settings.font_size or "medium",
                streamer_preset=settings.streamer_preset or "none",
                title_font_name=settings.title_font or settings.caption_font or "Outfit",
                font_size_px=settings.font_size_px,
                title_font_size_px=settings.title_font_size_px,
                title_text_case=settings.title_text_case or settings.text_case or "uppercase",
                title_x_percent=getattr(settings, "title_x_percent", 50.0),
                subtitle_offset_seconds=getattr(settings, "subtitle_offset_seconds", 0.0)
            )

        # 3. Render Final Vertical MP4
        clip_status["status"] = "rendering"
        clip_status["progress_percent"] = 70

        out_filename = f"clip_{idx+1}_{batch_id}.mp4"
        out_path = str(EXPORTS_DIR / out_filename)
        add_render_log(batch_id, f"Clip {idx + 1}: subtitle siap, memulai render FFmpeg", clip_index=idx)

        last_progress = {"timestamp": 0.0, "percent": -5}

        def _on_ffmpeg_progress(info: Dict[str, Any]):
            now = datetime.now().timestamp()
            percent = int(info.get("percent", 0))
            if now - last_progress["timestamp"] < 2 and percent < last_progress["percent"] + 5:
                return
            last_progress["timestamp"] = now
            last_progress["percent"] = percent
            add_render_log(
                batch_id,
                f"FFmpeg clip {idx + 1}: {percent}% | frame {info.get('frame', 0)} | "
                f"{float(info.get('fps', 0)):.1f} fps | time {float(info.get('time', 0)):.1f}s | speed {info.get('speed', '0x')}",
                level="progress",
                clip_index=idx
            )

        await asyncio.to_thread(
            render_clip_to_mp4,
            video_path=raw_path,
            output_mp4_path=out_path,
            aspect_ratio=settings.aspect_ratio,
            background_style=settings.background_style,
            enable_face_tracking=settings.enable_face_tracking,
            streamer_preset=settings.streamer_preset,
            facecam_position=getattr(settings, "facecam_position", "auto") or "auto",
            title_text=display_title if not skip_ass_title else None,
            title_position=settings.title_position,
            ass_subtitles_path=ass_path,
            clip_duration=duration_sec,
            title_overlay_path=title_overlay_path,
            title_duration=settings.title_duration if settings.title_duration else "entire",
            watermark_enabled=bool(settings.watermark_enabled),
            watermark_type=settings.watermark_type or "image",
            watermark_image_path=settings.watermark_file_path,
            watermark_text=settings.watermark_text,
            watermark_size=float(settings.watermark_size if settings.watermark_size is not None else 20.0),
            watermark_opacity=float((settings.watermark_opacity if settings.watermark_opacity is not None else 80.0) / 100.0),
            watermark_x_percent=float(settings.watermark_x if settings.watermark_x is not None else 90.0),
            watermark_y_percent=float(settings.watermark_y if settings.watermark_y is not None else 8.0),
            bgm_enabled=bool(settings.bgm_enabled),
            bgm_path=settings.bgm_file_path,
            bgm_volume=float((settings.bgm_volume if settings.bgm_volume is not None else 25.0) / 100.0),
            bgm_start_offset=float(settings.bgm_start_offset or 0.0),
            hook_sfx_enabled=bool(settings.hook_sfx_enabled),
            hook_sfx_path=settings.hook_sfx_file_path,
            hook_sfx_volume=float((settings.hook_sfx_volume if settings.hook_sfx_volume is not None else 100.0) / 100.0),
            original_audio_volume=float((settings.original_audio_volume if settings.original_audio_volume is not None else 100.0) / 100.0),
            hardware_accel=settings.hardware_accel or "auto",
            title_y_percent=settings.title_y_percent,
            crop_x_percent=getattr(settings, "crop_x_percent", None),
            title_x_percent=getattr(settings, "title_x_percent", 50.0),
            progress_callback=_on_ffmpeg_progress
        )

        if not os.path.exists(out_path) or not is_valid_mp4(out_path):
            raise RuntimeError("Rendered MP4 file is incomplete or missing. Please retry rendering.")

        clip_status["status"] = "completed"
        clip_status["progress_percent"] = 100
        add_render_log(batch_id, f"Clip {idx + 1}: render selesai dan file MP4 valid", level="success", clip_index=idx)
        clip_status["download_url"] = f"/api/download-rendered/{out_filename}"
        clip_status["output_path"] = out_path

    except Exception as e:
        failed_phase = clip_status.get("status")
        add_render_log(batch_id, f"Clip {idx + 1}: ERROR - {e}", level="error", clip_index=idx)
        logger.error(f"Error rendering clip {idx} in batch {batch_id}: {e}")
        clip_status["status"] = "error"
        err_msg = str(e)
        if "moov atom not found" in err_msg.lower():
            err_msg = "Download interrupted by internet lag ('moov atom not found'). Click Retry to re-download."
        elif "timed out" in err_msg.lower() or "timeout" in err_msg.lower():
            if failed_phase == "rendering":
                err_msg = "Video rendering timed out. Try switching to 'Universal CPU (libx264)' in Studio Settings or retry."
            else:
                err_msg = "Video download timed out due to slow/laggy internet connection. Click Retry to try again."
        clip_status["error_message"] = err_msg
        clip_status["error"] = err_msg

        # Clean up any partial raw video
        if raw_path and os.path.exists(raw_path):
            try:
                os.unlink(raw_path)
            except Exception:
                pass


def update_batch_summary_and_zip(batch_id: str, settings: RenderSettingsModel):
    """
    Updates the batch ZIP archive and computes overall status and friendly messages.
    """
    batch = RENDER_BATCHES.get(batch_id)
    if not batch:
        return

    # Generate/update ZIP bundle for the batch with title-based filenames and duplicate handling
    try:
        completed_clips = [c for c in batch["clips"] if c.get("status") == "completed" and c.get("download_url")]
        if completed_clips:
            zip_filename = f"cheat_clip_pro_{batch_id}.zip"
            zip_path = EXPORTS_DIR / zip_filename
            title_counts: Dict[str, int] = {}
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                for c in completed_clips:
                    fname = c["download_url"].split("?")[0].split("/")[-1]
                    fpath = EXPORTS_DIR / fname
                    if fpath.exists():
                        raw_title = (c.get("base_title") or c.get("title") or "").strip()
                        clean_title = re.sub(r'[\\/*?:"<>|]', "", raw_title) or f"clip_{c.get('clip_index', 1)}"
                        fn_pfx = re.sub(r'[\\/*?:"<>|]', "", settings.file_name_prefix or "")
                        fn_sfx = re.sub(r'[\\/*?:"<>|]', "", settings.file_name_suffix or "")
                        formatted_name = f"{fn_pfx}{clean_title}{fn_sfx}".strip() or clean_title
                        count = title_counts.get(formatted_name, 0)
                        title_counts[formatted_name] = count + 1
                        arc_name = f"{formatted_name}.mp4" if count == 0 else f"{formatted_name} ({count}).mp4"
                        zipf.write(fpath, arcname=arc_name)
            batch["zip_url"] = f"/api/download-batch-zip/{batch_id}"
        else:
            batch["zip_url"] = None
    except Exception as e:
        logger.warning(f"Failed to create batch zip: {e}")

    # Determine overall status and error messaging
    failed_clips = [c for c in batch["clips"] if c.get("status") == "error"]
    running_clips = [c for c in batch["clips"] if c.get("status") in ["downloading", "transcribing", "rendering", "pending"]]

    if running_clips:
        batch["overall_status"] = "running"
    elif len(failed_clips) == len(batch["clips"]):
        batch["overall_status"] = "error"
        batch["error_message"] = f"All {len(batch['clips'])} clip(s) failed. You can click 'Retry' to try again."
    elif len(failed_clips) > 0:
        batch["overall_status"] = "completed"
        batch["warning_message"] = f"{len(failed_clips)} of {len(batch['clips'])} clips encountered errors. You can retry failed clips anytime."
    else:
        batch["overall_status"] = "completed"
        batch["warning_message"] = None


def _get_concat_stream_signature(file_path: str) -> Optional[Tuple[Tuple[str, ...], ...]]:
    """Return codec parameters required for safe concat-demuxer stream copy."""
    probe_cmd = [
        "ffprobe", "-v", "error", "-show_streams",
        "-show_data_hash", "sha256",
        "-show_entries",
        "stream=codec_type,codec_name,profile,codec_tag_string,width,height,pix_fmt,level,sample_rate,channels,channel_layout,time_base,avg_frame_rate,r_frame_rate,field_order,start_time,extradata_hash",
        "-of", "json", file_path,
    ]
    try:
        result = subprocess.run(
            probe_cmd, capture_output=True, text=True, timeout=20, check=False
        )
        if result.returncode != 0:
            return None
        streams = json.loads(result.stdout or "{}").get("streams", [])
        if not streams:
            return None
        signature = []
        for stream in streams:
            if stream.get("codec_type") not in ("video", "audio"):
                continue
            signature.append(tuple(
                str(stream.get(key) or "")
                for key in (
                    "codec_type", "codec_name", "profile", "codec_tag_string",
                    "width", "height", "pix_fmt", "level", "sample_rate",
                    "channels", "channel_layout", "time_base",
                    "avg_frame_rate", "r_frame_rate", "field_order", "start_time",
                    "extradata_hash",
                )
            ))
        return tuple(signature) if signature else None
    except (OSError, subprocess.SubprocessError, ValueError, TypeError):
        return None


def _try_concat_segments_stream_copy(
    part_paths: List[str], output_path: str, timeout: int
) -> bool:
    """Fast-path compatible MP4 segments with the concat demuxer (no re-encode)."""
    if len(part_paths) < 2:
        return False

    signatures = [_get_concat_stream_signature(path) for path in part_paths]
    if not signatures[0] or any(sig != signatures[0] for sig in signatures[1:]):
        return False

    list_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", suffix=".ffconcat",
            prefix="concat_", dir=str(TEMP_DIR), delete=False
        ) as list_file:
            list_path = list_file.name
            list_file.write("ffconcat version 1.0\n")
            for part_path in part_paths:
                escaped_path = os.path.abspath(part_path).replace("\\", "\\\\").replace("'", "\\'")
                list_file.write(f"file '{escaped_path}'\n")

        command = [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-f", "concat", "-safe", "0", "-i", list_path,
            "-map", "0:v:0", "-map", "0:a:0?",
            "-c", "copy", "-movflags", "+faststart",
            output_path,
        ]
        result = subprocess.run(
            command, capture_output=True, text=True,
            timeout=timeout, check=False,
        )
        if result.returncode != 0 or not is_valid_mp4(output_path):
            if os.path.exists(output_path):
                os.unlink(output_path)
            logger.warning(
                "Fast merged concat (stream copy) was unavailable; "
                "falling back to normalized FFmpeg encoding: %s",
                (result.stderr or result.stdout or "invalid output")[-1200:],
            )
            return False

        logger.info(
            "Merged %d compatible segments using stream copy (no video re-encode).",
            len(part_paths),
        )
        return True
    except (OSError, subprocess.SubprocessError) as exc:
        if os.path.exists(output_path):
            try:
                os.unlink(output_path)
            except OSError:
                pass
        logger.warning("Fast merged concat failed; using safe re-encode fallback: %s", exc)
        return False
    finally:
        if list_path and os.path.exists(list_path):
            try:
                os.unlink(list_path)
            except OSError:
                pass


async def render_merged_batch_clips(
    batch_id: str,
    clips: List[Dict[str, Any]],
    settings: RenderSettingsModel,
    target_url: str,
    transcript: Optional[List[Dict[str, Any]]] = None,
    cookies_content: Optional[str] = None
):
    batch = RENDER_BATCHES.get(batch_id)
    if not batch:
        return

    clip_status = batch["clips"][0]
    clip_status["status"] = "downloading"
    clip_status["progress_percent"] = 10
    clip_status["error_message"] = None
    clip_status["error"] = None

    part_paths: List[str] = []
    raw_merged_path: Optional[str] = None
    ass_path: Optional[str] = None
    title_overlay_path: Optional[str] = None

    try:
        total_segments = len(clips)
        add_render_log(batch_id, f"Merged: mulai mengunduh {total_segments} segmen", clip_index=0)
        # 1. Download / slice each segment
        for i, seg in enumerate(clips):
            add_render_log(batch_id, f"Merged: mengunduh segmen {i + 1}/{total_segments}", clip_index=0)
            clip_status["progress_percent"] = 10 + int((i / max(1, total_segments)) * 25)
            s_t = float(seg.get("start_time", 0.0))
            e_t = float(seg.get("end_time", s_t + 30.0))
            part_filename = f"{batch_id}_part_{i}_raw.mp4"
            def _on_merged_download_progress(info: Dict[str, Any]):
                percent = max(0.0, min(100.0, float(info.get("percent", 0) or 0)))
                clip_status["download_percent"] = percent
                clip_status["downloaded"] = info.get("downloaded", "")
                clip_status["download_total"] = info.get("total", "")
                clip_status["download_speed"] = info.get("speed", "")
                clip_status["download_eta"] = info.get("eta", "")
                clip_status["progress_percent"] = 10 + int(((i + percent / 100.0) / max(1, total_segments)) * 25)

            p_path = await asyncio.to_thread(
                download_clip_segment,
                target_url,
                s_t,
                e_t,
                part_filename,
                cookies_content,
                _on_merged_download_progress
            )
            if not p_path or not os.path.exists(p_path) or not is_valid_mp4(p_path):
                raise RuntimeError(
                    f"Segment #{i+1} ({s_t:.1f}s - {e_t:.1f}s) is incomplete or corrupted. Please retry rendering."
                )
            part_paths.append(p_path)

        # 2. Concatenate raw video segments
        clip_status["status"] = "transcribing"
        clip_status["progress_percent"] = 40
        add_render_log(batch_id, "Merged: segmen selesai diunduh, mulai penggabungan", clip_index=0)

        raw_merged_filename = f"{batch_id}_merged_raw.mp4"
        raw_merged_path = str(TEMP_DIR / raw_merged_filename)

        # Normalize stream layout first, then measure each real downloaded segment.
        # Requested source in/out points are not reliable durations after keyframe slicing.
        segment_durations: List[float] = []
        for idx_p, segment_path in enumerate(part_paths):
            add_render_log(
                batch_id,
                f"Merged: memeriksa stream segmen {idx_p + 1}/{len(part_paths)}",
                clip_index=0,
            )
            await asyncio.to_thread(_ensure_concat_streams, segment_path)
            measured_duration = await asyncio.to_thread(
                _probe_media_duration, segment_path
            )
            segment_durations.append(measured_duration)
            logger.info(
                "MERGED SEGMENT TIMING | index=%d | file=%s | actual_duration=%.3fs",
                idx_p + 1, Path(segment_path).name, measured_duration,
            )

        expected_concat_duration = sum(segment_durations)

        if len(part_paths) == 1:
            raw_merged_path = part_paths[0]
        else:
            concat_timeout = max(180, total_segments * 60)
            logger.info(f"Concatenating {len(part_paths)} segments into {raw_merged_path}")

            # Prefer packet-level stream copy when every segment has identical
            # codec parameters. This avoids an expensive intermediate encode.
            copied = await asyncio.to_thread(
                _try_concat_segments_stream_copy,
                part_paths,
                raw_merged_path,
                concat_timeout,
            )

            if copied:
                add_render_log(
                    batch_id,
                    "Merged: segmen kompatibel, digabung tanpa encode ulang",
                    level="success",
                    clip_index=0,
                )
            else:
                inputs = []
                filter_parts = []
                for idx_p, p in enumerate(part_paths):
                    inputs.extend(["-i", p])
                    filter_parts.append(
                        f"[{idx_p}:v]"
                        f"scale=1280:720:force_original_aspect_ratio=decrease,"
                        f"pad=1280:720:(ow-iw)/2:(oh-ih)/2,"
                        f"setsar=1,fps=30,format=yuv420p,setpts=PTS-STARTPTS"
                        f"[v{idx_p}];"
                        f"[{idx_p}:a]aresample=48000:async=1:first_pts=0,"
                        f"aformat=sample_fmts=fltp:channel_layouts=stereo,"
                        f"asetpts=PTS-STARTPTS[a{idx_p}];"
                    )

                concat_inputs = "".join(
                    f"[v{idx_p}][a{idx_p}]"
                    for idx_p in range(len(part_paths))
                )
                filter_str = (
                    f"{''.join(filter_parts)}"
                    f"{concat_inputs}concat=n={len(part_paths)}:v=1:a=1[v][a]"
                )
                concat_cmd = [
                    "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                    *inputs,
                    "-filter_complex", filter_str,
                    "-map", "[v]", "-map", "[a]",
                    "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18",
                    "-c:a", "aac", "-b:a", "192k",
                    "-avoid_negative_ts", "make_zero",
                    "-movflags", "+faststart",
                    raw_merged_path
                ]
                concat_result = await asyncio.to_thread(
                    subprocess.run,
                    concat_cmd,
                    capture_output=True,
                    text=True,
                    timeout=concat_timeout,
                    check=False,
                )
                if concat_result.returncode != 0 or not is_valid_mp4(raw_merged_path):
                    ffmpeg_error = (
                        concat_result.stderr
                        or concat_result.stdout
                        or "Tidak ada detail error dari FFmpeg"
                    ).strip()
                    raise RuntimeError(
                        f"FFmpeg concat gagal (exit {concat_result.returncode}): "
                        f"{ffmpeg_error[-4000:]}"
                    )
                add_render_log(
                    batch_id,
                    "Merged: seluruh segmen berhasil dinormalisasi dan digabung",
                    level="success",
                    clip_index=0,
                )

        # Verify the produced timeline before assigning subtitle offsets.
        raw_merged_duration = await asyncio.to_thread(
            _probe_media_duration, raw_merged_path
        )
        concat_tolerance = max(1.0, expected_concat_duration * 0.01)
        concat_drift = abs(raw_merged_duration - expected_concat_duration)
        add_render_log(
            batch_id,
            f"Merged: durasi aktual {raw_merged_duration:.2f}s; "
            f"akumulasi segmen {expected_concat_duration:.2f}s",
            level="info",
            clip_index=0,
        )
        if concat_drift > concat_tolerance:
            raise RuntimeError(
                "Durasi hasil concat tidak cocok dengan total durasi segmen "
                f"(hasil={raw_merged_duration:.3f}s, "
                f"total_segmen={expected_concat_duration:.3f}s, "
                f"selisih={concat_drift:.3f}s, "
                f"toleransi={concat_tolerance:.3f}s). "
                "Render dihentikan agar subtitle dan audio tidak bergeser."
            )

        add_render_log(batch_id, "Merged: mulai transkripsi dan pembuatan subtitle", clip_index=0)
        # 3. Transcribe & generate time-shifted subtitles
        target_lang = None
        if transcript:
            try:
                from backend.utils.text import detect_transcript_language
                detected = detect_transcript_language(transcript[:50])
                if detected and detected.get("code") in ("id", "en"):
                    target_lang = detected["code"]
            except Exception:
                pass

        total_duration_sec = 0.0
        merged_words = []
        for i, seg in enumerate(clips):
            s_t = float(seg.get("start_time", 0.0))
            e_t = float(seg.get("end_time", s_t + 30.0))
            # Word timestamps are clip-relative; shift by the measured media
            # duration, not the requested source interval.
            seg_dur = segment_durations[i]
            if settings.caption_style != "none":
                seg_words = await asyncio.to_thread(
                    transcribe_clip_words,
                    part_paths[i],
                    transcript,
                    s_t,
                    e_t,
                    target_lang
                )
                for w in seg_words:
                    w_copy = dict(w)
                    w_start = float(w.get("start", 0.0))
                    w_end = float(w.get("end", w_start + 0.15))
                    w_copy["start"] = round(total_duration_sec + max(0.0, w_start), 3)
                    w_copy["end"] = round(max(w_copy["start"] + 0.1, total_duration_sec + max(0.0, w_end)), 3)
                    merged_words.append(w_copy)
            total_duration_sec += seg_dur

        total_duration_sec = max(1.0, total_duration_sec)

        display_title = clip_status.get("title") or clip_status.get("base_title") or "Highlight Video"
        skip_ass_title = False

        if display_title and settings.title_position != "none" and has_emoji(display_title):
            title_png_filename = f"{batch_id}_merged_title.png"
            title_png_path = str(TEMP_DIR / title_png_filename)
            try:
                canvas_w = 1920 if (settings.aspect_ratio == "16:9_landscape") else 1080
                canvas_h = 1080 if (settings.aspect_ratio == "16:9_landscape") else 1920
                rendered_overlay = await asyncio.to_thread(
                    render_title_overlay_png,
                    title_text=display_title,
                    output_png_path=title_png_path,
                    font_name=settings.title_font or settings.caption_font or "Outfit",
                    target_aspect_ratio=settings.aspect_ratio or "9:16",
                    font_size_preset=settings.title_font_size or settings.font_size or "medium",
                    text_case=settings.title_text_case or settings.text_case or "uppercase",
                    title_position=settings.title_position or "auto",
                    title_y_percent=settings.title_y_percent,
                    canvas_w=canvas_w,
                    canvas_h=canvas_h,
                    title_font_size_preset=settings.title_font_size or settings.font_size or "medium",
                    streamer_preset=settings.streamer_preset or "none",
                    title_font_name=settings.title_font or settings.caption_font or "Outfit",
                    title_font_size_px=settings.title_font_size_px,
                    title_text_case=settings.title_text_case or settings.text_case or "uppercase",
                    title_x_percent=getattr(settings, "title_x_percent", 50.0)
                )
                if rendered_overlay and os.path.exists(rendered_overlay):
                    title_overlay_path = rendered_overlay
                    skip_ass_title = True
            except Exception as ex:
                logger.warning(f"Could not render color emoji title overlay for merged clip: {ex}")
                skip_ass_title = False

        if settings.caption_style != "none" or (display_title and settings.title_position != "none" and not skip_ass_title):
            ass_filename = f"{batch_id}_merged.ass"
            ass_path = str(TEMP_DIR / ass_filename)
            await asyncio.to_thread(
                generate_ass_file,
                words=merged_words,
                style_preset=settings.caption_style,
                font_name=settings.caption_font or "Outfit",
                output_ass_path=ass_path,
                target_aspect_ratio=settings.aspect_ratio,
                font_size_preset=settings.font_size,
                text_case=settings.text_case,
                title_text=display_title if not skip_ass_title else None,
                title_position=settings.title_position,
                title_duration=settings.title_duration if settings.title_duration else "entire",
                duration_seconds=total_duration_sec,
                title_y_percent=settings.title_y_percent,
                subtitle_y_percent=settings.subtitle_y_percent,
                subtitle_position_mode=settings.subtitle_position_mode if settings.subtitle_position_mode else "bottom",
                subtitle_center_y_percent=settings.subtitle_center_y_percent if settings.subtitle_center_y_percent is not None else 50.0,
                skip_title=skip_ass_title,
                title_font_size_preset=settings.title_font_size or settings.font_size or "medium",
                streamer_preset=settings.streamer_preset or "none",
                title_font_name=settings.title_font or settings.caption_font or "Outfit",
                font_size_px=settings.font_size_px,
                title_font_size_px=settings.title_font_size_px,
                title_text_case=settings.title_text_case or settings.text_case or "uppercase"
            )

        # 4. Render Final Single MP4
        clip_status["status"] = "rendering"
        clip_status["progress_percent"] = 65

        clean_safe_title = re.sub(r'[\\/*?:"<>|]', "", clip_status.get("base_title") or "highlight_compilation")
        clean_safe_title = clean_safe_title.replace(" ", "_")[:40] or "compilation"
        out_filename = f"compilation_{clean_safe_title}_{batch_id}.mp4"
        out_path = str(EXPORTS_DIR / out_filename)
        add_render_log(batch_id, "Merged: subtitle siap, memulai render FFmpeg", clip_index=0)

        last_progress = {"timestamp": 0.0, "percent": -5}

        def _on_ffmpeg_progress(info: Dict[str, Any]):
            now = datetime.now().timestamp()
            percent = int(info.get("percent", 0))
            if now - last_progress["timestamp"] < 2 and percent < last_progress["percent"] + 5:
                return
            last_progress["timestamp"] = now
            last_progress["percent"] = percent
            add_render_log(
                batch_id,
                f"FFmpeg merged: {percent}% | frame {info.get('frame', 0)} | "
                f"{float(info.get('fps', 0)):.1f} fps | time {float(info.get('time', 0)):.1f}s | speed {info.get('speed', '0x')}",
                level="progress",
                clip_index=0
            )

        await asyncio.to_thread(
            render_clip_to_mp4,
            video_path=raw_merged_path,
            output_mp4_path=out_path,
            aspect_ratio=settings.aspect_ratio,
            background_style=settings.background_style,
            enable_face_tracking=settings.enable_face_tracking,
            streamer_preset=settings.streamer_preset,
            facecam_position=getattr(settings, "facecam_position", "auto") or "auto",
            title_text=display_title if not skip_ass_title else None,
            title_position=settings.title_position,
            ass_subtitles_path=ass_path,
            clip_duration=total_duration_sec,
            title_overlay_path=title_overlay_path,
            title_duration=settings.title_duration if settings.title_duration else "entire",
            watermark_enabled=bool(settings.watermark_enabled),
            watermark_type=settings.watermark_type or "image",
            watermark_image_path=settings.watermark_file_path,
            watermark_text=settings.watermark_text,
            watermark_size=float(settings.watermark_size if settings.watermark_size is not None else 20.0),
            watermark_opacity=float((settings.watermark_opacity if settings.watermark_opacity is not None else 80.0) / 100.0),
            watermark_x_percent=float(settings.watermark_x if settings.watermark_x is not None else 90.0),
            watermark_y_percent=float(settings.watermark_y if settings.watermark_y is not None else 8.0),
            bgm_enabled=bool(settings.bgm_enabled),
            bgm_path=settings.bgm_file_path,
            bgm_volume=float((settings.bgm_volume if settings.bgm_volume is not None else 25.0) / 100.0),
            bgm_start_offset=float(settings.bgm_start_offset or 0.0),
            hook_sfx_enabled=bool(settings.hook_sfx_enabled),
            hook_sfx_path=settings.hook_sfx_file_path,
            hook_sfx_volume=float((settings.hook_sfx_volume if settings.hook_sfx_volume is not None else 100.0) / 100.0),
            original_audio_volume=float((settings.original_audio_volume if settings.original_audio_volume is not None else 100.0) / 100.0),
            hardware_accel=settings.hardware_accel or "auto",
            title_y_percent=settings.title_y_percent,
            crop_x_percent=getattr(settings, "crop_x_percent", None),
            title_x_percent=getattr(settings, "title_x_percent", 50.0),
            progress_callback=_on_ffmpeg_progress
        )

        if not os.path.exists(out_path) or not is_valid_mp4(out_path):
            raise RuntimeError("Merged MP4 file is incomplete or missing. Please retry rendering.")

        final_duration = await asyncio.to_thread(_probe_media_duration, out_path)
        final_tolerance = max(1.0, raw_merged_duration * 0.01)
        final_drift = abs(final_duration - raw_merged_duration)
        if final_drift > final_tolerance:
            raise RuntimeError(
                "Durasi video akhir berubah terlalu jauh setelah proses render "
                f"(raw={raw_merged_duration:.3f}s, final={final_duration:.3f}s, "
                f"selisih={final_drift:.3f}s)."
            )

        clip_status["status"] = "completed"
        clip_status["progress_percent"] = 100
        add_render_log(batch_id, "Merged: render selesai dan file MP4 valid", level="success", clip_index=0)
        clip_status["download_url"] = f"/api/download-rendered/{out_filename}"
        clip_status["output_path"] = out_path

    except Exception as e:
        add_render_log(batch_id, f"Merged: ERROR - {e}", level="error", clip_index=0)
        logger.error(f"Error rendering merged batch {batch_id}: {e}")
        clip_status["status"] = "error"
        err_msg = str(e)
        clip_status["error_message"] = err_msg
        clip_status["error"] = err_msg

    finally:
        for p in part_paths:
            if p and os.path.exists(p) and p != raw_merged_path:
                try:
                    os.unlink(p)
                except Exception:
                    pass
        if raw_merged_path and os.path.exists(raw_merged_path):
            try:
                os.unlink(raw_merged_path)
            except Exception:
                pass


async def process_batch_rendering(batch_id: str, request: RenderBatchRequest):
    async with _RENDER_SEMAPHORE:
        batch = RENDER_BATCHES.get(batch_id)
        if not batch:
            return

        clips = request.clips
        settings = request.settings

        # Normalize video URL for history or direct URL
        target_url = (request.video_url or "").strip()
        if "yt_audio_" in target_url:
            match_yt = re.search(r'yt_audio_([a-zA-Z0-9_-]{11})', target_url)
            if match_yt:
                target_url = f"https://www.youtube.com/watch?v={match_yt.group(1)}"
        elif request.video_id and (request.video_id.startswith("gdrive_") or request.video_id.startswith("upload_")):
            if not target_url.startswith("/api/video/"):
                target_url = f"/api/video/{request.video_id}"
        elif request.video_id and is_twitch_url(request.video_id):
            tw_info = extract_twitch_info(request.video_id)
            target_url = get_twitch_canonical_url(tw_info) if tw_info else request.video_id
        elif target_url and is_twitch_url(target_url):
            tw_info = extract_twitch_info(target_url)
            target_url = get_twitch_canonical_url(tw_info) if tw_info else target_url
        elif not target_url:
            if request.video_id:
                target_url = f"https://www.youtube.com/watch?v={request.video_id}"
        elif not target_url.startswith("http") and not target_url.startswith("/api/video/"):
            target_url = f"https://www.youtube.com/watch?v={target_url}"

        cookies_content = getattr(request, "cookies", None)
        is_merged = bool(settings and getattr(settings, "render_mode", "separate") == "merged")
        if is_merged:
            batch["current_clip_index"] = 0
            await render_merged_batch_clips(
                batch_id=batch_id,
                clips=clips,
                settings=settings,
                target_url=target_url,
                transcript=request.transcript,
                cookies_content=cookies_content
            )
            batch["current_clip_index"] = 1
        else:
            for idx, clip in enumerate(clips):
                batch["current_clip_index"] = idx
                await render_single_batch_clip(
                    batch_id=batch_id,
                    idx=idx,
                    clip=clip,
                    settings=settings,
                    target_url=target_url,
                    transcript=request.transcript,
                    total_clips=len(clips),
                    cookies_content=cookies_content
                )
                batch["current_clip_index"] = idx + 1

        update_batch_summary_and_zip(batch_id, settings)


async def process_batch_retry(batch_id: str, clip_indices: List[int]):
    async with _RENDER_SEMAPHORE:
        batch = RENDER_BATCHES.get(batch_id)
        request = BATCH_REQUESTS.get(batch_id)
        if not batch or not request:
            logger.error(f"Cannot retry batch {batch_id}: batch or request data not found")
            return

        batch["overall_status"] = "running"
        clips = request.clips
        settings = request.settings
        target_url = (request.video_url or "").strip()
        if "yt_audio_" in target_url:
            match_yt = re.search(r'yt_audio_([a-zA-Z0-9_-]{11})', target_url)
            if match_yt:
                target_url = f"https://www.youtube.com/watch?v={match_yt.group(1)}"
        elif request.video_id and (request.video_id.startswith("gdrive_") or request.video_id.startswith("upload_")):
            if not target_url.startswith("/api/video/"):
                target_url = f"/api/video/{request.video_id}"
        elif not target_url:
            if request.video_id:
                target_url = f"https://www.youtube.com/watch?v={request.video_id}"
        elif not target_url.startswith("http") and not target_url.startswith("/api/video/"):
            target_url = f"https://www.youtube.com/watch?v={target_url}"

        cookies_content = getattr(request, "cookies", None)
        is_merged = bool(batch.get("is_merged")) or bool(settings and getattr(settings, "render_mode", "separate") == "merged")
        if is_merged:
            batch["current_clip_index"] = 0
            await render_merged_batch_clips(
                batch_id=batch_id,
                clips=clips,
                settings=settings,
                target_url=target_url,
                transcript=request.transcript,
                cookies_content=cookies_content
            )
            batch["current_clip_index"] = 1
        else:
            for idx in clip_indices:
                if 0 <= idx < len(clips):
                    batch["current_clip_index"] = idx
                    await render_single_batch_clip(
                        batch_id=batch_id,
                        idx=idx,
                        clip=clips[idx],
                        settings=settings,
                        target_url=target_url,
                        transcript=request.transcript,
                        total_clips=len(clips),
                        cookies_content=cookies_content
                    )

        update_batch_summary_and_zip(batch_id, settings)
