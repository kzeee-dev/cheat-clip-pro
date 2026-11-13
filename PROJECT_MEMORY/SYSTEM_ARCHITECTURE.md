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
