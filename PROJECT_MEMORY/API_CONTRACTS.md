# API Contracts

This document must describe actual request/response models and routes.
Do not invent endpoints or schemas.

## Known router groups
- analyze
- cookies
- downloads
- media
- render
- system

## Known frontend API entry
- src/utils/api.ts

## Audit required
- Enumerate all registered routes from backend source.
- Record HTTP method, path, request schema, response schema and errors.
- Record streaming/SSE event formats.
- Record frontend callers and compatibility constraints.
- Record authentication, cookie and proxy behavior where applicable.

Status: PENDING SOURCE AUDIT.


## Source-audited routes (2026-11-15)

| Method | Path | Purpose |
|---|---|---|
| GET | /api/health | Backend health |
| GET | /api/supadata-usage | Transcript provider usage |
| GET | /api/models | Gemini model list |
| GET | /api/openrouter-models | OpenRouter model list |
| POST | /api/analyze | Analyze source video |
| POST / GET / DELETE | /api/cookies | Save, inspect, delete YouTube cookies |
| POST | /api/download-raw-video | Start raw-video download |
| GET | /api/download-raw-status/{job_id} | Raw-video job status |
| POST | /api/download-raw-clip | Start raw-clip download |
| GET | /api/download-raw-clip-status/{job_id} | Raw-clip job status |
| POST | /api/upload-video | Upload source video |
| GET | /api/video/{file_name:path} | Stream source media (range support) |
| POST / GET | /api/upload-bgm, /api/audio/{file_name} | Upload/read background audio |
| POST | /api/upload-sfx | Upload hook sound effect |
| POST / GET | /api/upload-watermark, /api/watermark/{file_name} | Upload/read watermark |
| GET | /api/clip-frame | Extract preview frame |
| GET | /api/detect-face | Detect speaker face |
| POST / GET | /api/upload-font, /api/fonts, /api/font-file/{file_name} | Upload/list/read fonts |
| POST | /api/render-batch | Start separate or merged render |
| POST | /api/render-batch/{batch_id}/retry | Retry failed render clips |
| GET | /api/render-progress/{batch_id} | Render progress SSE |
| POST | /api/save-rendered-clip | Save browser-rendered MP4 |
| POST | /api/save-client-download | Save browser-rendered download artifact |
| GET | /api/download-client-file/{file_name} | Download client artifact |
| GET | /api/download-rendered/{file_name} | Download rendered MP4 |
| GET | /api/download-batch-zip/{batch_id} | Download render batch ZIP |
| GET | /api/hardware-accel | Hardware encoder capabilities |
| GET | /api/system/ping | Backend and internet connectivity |
| GET | /api/temp-storage-info | Temporary storage summary |
| POST | /api/clear-temp | Administrative temp cleanup |
| POST | /api/cleanup-expired-temp | Administrative age-based cleanup |
| POST | /api/auto-cleanup | Administrative TTL/quota cleanup |
| GET | /api/system/version | Git/runtime version |
| GET | /api/system/check-update | Check update availability |
| POST | /api/system/update | Administrative self-update (local mode only by default) |
| POST | /api/system/restart | Administrative restart (local mode only by default) |

Request/response field-level schemas and error contracts still need to be expanded from the Pydantic models and route implementations; this table is a route inventory, not a complete API specification.
