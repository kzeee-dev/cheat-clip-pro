# System Architecture

## Known high-level structure
- Frontend: React/TypeScript, entry point src/App.tsx.
- API utilities: src/utils/api.ts.
- Shared frontend types: src/types.ts.
- Backend: Python application.
- Backend routers include analyze, cookies, downloads, media, render, system.
- Backend services include AI, download, Google Drive, OpenRouter, render, system and YouTube services.
- Android integration: Capacitor / native Android Java activity.
- Media processing: FFmpeg and yt-dlp.

## Runtime environment notes
- User development environment: Android Termux with Ubuntu proot.
- Backend has used Uvicorn and FastAPI.
- A dedicated backend virtual environment was used for isolated media testing.
- Do not assume runtime paths or process IDs remain unchanged.

## Pending architecture audit
- Exact frontend-to-backend request flow.
- Complete router/service dependency map.
- Render pipeline and job lifecycle.
- AI provider selection and fallback.
- Android WebView and DownloadManager lifecycle.
- Configuration and environment variable inventory.


## Verified render pipeline (source audit, 2026-11-15)
- Studio state and editor preview: src/components/ClipStudioSection.tsx; preferences persisted under cheat_clip_studio_preferences.
- Submit callback: ClipStudioSection.onStartRender → src/App.tsx::handleStartBatchRender.
- Backend render request: POST /api/render-batch with RenderBatchRequest / RenderSettingsModel.
- Job lifecycle: backend/routers/render.py → backend/services/render_service.py::process_batch_rendering → separate or merged render path.
- Subtitle generation: backend/video_engine.py::generate_ass_file; final encoding: render_clip_to_mp4.
- Progress stream: GET /api/render-progress/{batch_id} (SSE).
- Final artifacts: /api/download-rendered/{file_name} and /api/download-batch-zip/{batch_id}.
- Android attachment handling: WebView DownloadListener → MainActivity opens the real attachment URL in Chrome; DownloadManager is a fallback when no browser is available.

## Operational notes
- Render batches and request objects are held in process memory (RENDER_BATCHES, BATCH_REQUESTS); a backend process restart loses active job state.
- A global render semaphore serializes render jobs to protect low-resource devices.
- Background cleanup uses configurable TTL/quota limits; verify active exports and retention before changing cleanup policy.
