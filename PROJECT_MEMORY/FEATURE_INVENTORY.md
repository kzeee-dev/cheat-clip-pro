# Feature Inventory

Status legend:
- PRESERVED: known existing feature; regression checks required.
- BASELINE: included in the user-accepted CI build.
- PENDING AUDIT: exact implementation or current test status not yet verified.

## Core application features
- Subtitle ON/OFF and persisted setting — PRESERVED
- Whisper transcription — PRESERVED
- Gemini visual analysis — PRESERVED
- Authentic video frame extraction — PRESERVED
- Single-video rendering — PRESERVED
- Batch rendering — PRESERVED
- Merged rendering — PRESERVED
- Live render terminal and progress — PRESERVED
- CPU fallback — PRESERVED
- Audio synchronization — PRESERVED
- Silent-segment handling — PRESERVED
- Smart Face Tracking — PRESERVED
- YouTube download fallback — PRESERVED
- Cookie normalization — PRESERVED
- Preview and MP4/ZIP/PKG downloads — PRESERVED
- Download status and network-stall handling — PRESERVED
- Capacitor, frontend/backend, API and WebView integration — PRESERVED
- FFmpeg/audio compatibility — PRESERVED
- Android native download integration — PENDING AUDIT
- Copywriting quality improvements — PENDING AUDIT

## Important regression rule
A feature is not considered verified merely because it appears in this inventory.
Record the exact test and result in SESSION_LOG.md or REGRESSION_CHECKLIST.md.
