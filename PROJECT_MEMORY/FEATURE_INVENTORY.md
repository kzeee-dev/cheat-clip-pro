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


## Auto Clipper Studio — work branch implementation (2026-11-13)
- Caption Motion Lab panel — IMPLEMENTED; frontend/backend build passed; real-media/device verification pending.
- Smart keyword highlight suggestions from AI key quotes and transcript context — IMPLEMENTED; original transcript is presentation-only and unchanged.
- Manual keyword overrides and custom highlight color — IMPLEMENTED; build passed; real-media/device verification pending.
- Motion presets: Static, Cinematic, Punch Impact, Smooth Pop, Kinetic Flow, Bounce Pro, Glitch Pro, Type Reveal, Slide Motion, Focus Zoom — IMPLEMENTED in ASS renderer; verification pending.
- Advanced caption stroke, shadow, glow, background box/opacity, and letter spacing — IMPLEMENTED in ASS renderer; verification pending.
