# Changelog

## 2026-11-12 — Media source resilience
Branch: fix/media-source-resilience

### Commit c48eb09
- Prefer yt-dlp Python module invocation over a potentially broken executable wrapper.
- CI Android APK workflow succeeded in GitHub Actions run #142.
- User accepted the resulting build as the perfect current baseline.

### Earlier work on this branch
- Improved YouTube metadata fallback.
- Added isolated player-client attempts and proxy/direct fallback.
- Added audio-file validation.
- Improved authentic frame extraction and rejected thumbnail/stale-frame fallback.
- Detailed implementation is recorded in Git history; verify exact commit history before further changes.

## 2026-11-12 — Main repository local changes
Branch: integrate/visual-analysis-android
Base commit: 2abd079
Status: UNCOMMITTED — DO NOT DISCARD

Files:
- android/app/src/main/AndroidManifest.xml
- android/app/src/main/java/com/kzeee/cheatclippro/MainActivity.java
- backend/routers/analyze.py
- backend/schemas/analyze.py
- backend/services/openrouter_service.py
- backend/utils/text.py

Summary:
- Android notification permission and native DownloadManager flow.
- AI copywriting prompt improvements.
- Transcript-grounded fallback title, caption and hashtags.
- Improved schema descriptions for generated copy.
- OpenRouter copywriting rules.
- More conservative first-person title sanitization.

These local changes are not part of commit c48eb09 unless later verified in Git history.


## 2026-11-12 — Fix first-person title sanitizer regex

- File: `backend/utils/text.py`
- Scope: `sanitize_first_person_title()` only.
- Fixed double-escaped regex whitespace (`\\s`), word boundary (`\\b`), and capture-group replacement (`\\1`).
- Improved the `What I think [about]...` transformation to produce `Thoughts on ...`, avoiding duplicated "about".
- Preserved neutral titles unchanged.
- Backup: `backend/utils/text.py.before_sanitizer_regex_fix_20261112_162549`.
- Validation: 13/13 targeted regression cases passed; `py_compile` passed; `git diff --check` passed.
- No commit or APK build performed. Backend/device runtime validation remains pending.


## 2026-11-12 — Distinct fallback title suggestion

- File: `backend/routers/analyze.py`
- Scope: transcript-based fallback clip title suggestion only.
- Changed `title_suggestion` so it uses a distinct phrase from a later sentence or a phrase following punctuation in the first sentence.
- If no distinct phrase of at least two words is available, the suggestion remains empty; the frontend can fall back to the main title.
- Existing title, caption, hashtags, timestamps, score, AI parsing path, frontend, and rendering logic were not intentionally changed by this patch.
- Backup: `backend/routers/analyze.py.before_distinct_fallback_titles_20261112_163408`.
- Validation: three targeted behavior cases passed; `python -m py_compile backend/routers/analyze.py` passed; `git diff --check` passed.
- No commit, APK build, live backend test, or Android device test performed.
- Accepted baseline build #142 (`c48eb09`) remains untouched.


## 2026-11-13 — Snapshot branch build and Studio editor foundation
Branch: `snapshot/phone-project-2026-11-13`

### CI enablement
- Added the snapshot branch to the existing Android debug-build workflow push filter; existing branch triggers and build steps were preserved.
- Snapshot commit `cac6ca6` triggered GitHub Actions run #168; backend syntax, frontend build, Capacitor sync, Gradle debug APK and artifact upload all passed.

### Auto Clipper Studio UI
- Added responsive workspace rules for phone portrait, compact landscape and tablet widths, including safe-area spacing, touch targets, and reduced-motion support.
- Added `src/components/StudioTimeline.tsx`: a video-duration track, transcript caption blocks, live playhead and tap-to-seek caption markers.
- Integrated the timeline into the existing Clip Studio player controls without replacing the current scrubber or render pipeline.
- Preserved the existing preview player, caption generation, selected clips, rendering settings and backend contracts.

### Verification
- GitHub Actions run #169 passed for the responsive CSS change.
- GitHub Actions run #172 passed for the integrated timeline and CSS. Frontend TypeScript/Vite build, Capacitor sync, Android Gradle `assembleDebug`, and APK artifact upload all completed successfully.
- Debug APK artifact: 4,027,844 bytes; SHA-256 `0b90ca0880d491acebe4989e232ee7baaa277a8fee62451315e8db8fbad49b21`.
- Runs #170 and #171 were cancelled by the workflow's existing per-branch concurrency rule when newer commits superseded them; the latest run #172 succeeded.

### Pending
- Physical Android device validation: portrait/landscape, timeline marker seeking, playback, caption preview, downloads and rendering regressions.
- AI keyword highlighting, motion presets, advanced text effects and deeper editor layout remain planned; not yet implemented.
- The accepted baseline branch `fix/media-source-resilience` and release signing configuration were not modified.


## 2026-11-15 — Clip Studio preview/render parity audit
Branch: audit/render-parity-2026-11-15

### Findings and changes
- The editor preview used hard-coded ease-out, did not apply the motion-intensity slider to animation amplitude, and treated line scope as a first-word animation.
- The preview multiplied active-word emphasis by the global text scale, while the ASS renderer only scaled the caption font.
- The ASS renderer applied word motion to the entire caption chunk and blended selected AI/gradient colors with white even though the UI labels the intensity control as detection intensity.
- Updated the preview to use the selected easing, intensity-derived CSS variables, and distinct word/line motion scope. Kept the 8% active-word emphasis separate from global text scaling.
- Updated ASS generation to scope word motion to the active word, apply line motion consistently to all words, preserve the selected highlight/gradient colors, and match the active-word emphasis.
- Added the isolated audit branch to the Android CI push filter.

### Files changed
- src/components/ClipStudioSection.tsx
- src/styles/studio-controls.css
- backend/video_engine.py
- .github/workflows/build-android.yml

### Validation
- GitHub Actions run 43719834072: SUCCESS.
- Python compileall, frontend TypeScript/Vite build, Capacitor sync, Gradle assembleDebug, and APK artifact upload all passed.
- Artifact: Cheat-Clip-Pro-Debug-APK, 4,033,210 bytes; SHA-256 cfe9e542432680cae15d508030741a6c899fdfcacd8cf15556cd62eb87dc85f3.
- Physical Android/Termux render tests are still pending; CI success is not proof of visual parity or runtime behavior.

### Security audit finding (not changed in this session)
- verify_admin_access() permits unauthenticated administrative requests when neither ADMIN_API_KEY nor CHEAT_CLIP_API_KEY is set.
- The Termux helper, desktop backend launcher and Docker configuration bind Uvicorn to 0.0.0.0; server deployments may therefore expose admin cleanup/update/restart routes without an API key.
- This requires a separate compatibility-aware security fix. Do not silently change local desktop behavior before confirming server-mode expectations.
