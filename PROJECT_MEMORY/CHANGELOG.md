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


## 2026-11-13 — Auto Clipper Studio caption motion foundation

Branch: work/auto-clipper-studio

- Added a collapsible Caption Motion Lab panel to the existing Studio workspace.
- Added smart keyword suggestions sourced from AI-selected key quotes and transcript context; source transcript text is not modified.
- Added manual highlight terms, selectable highlight color, nine motion presets plus static mode, and adjustable outline, shadow, glow, background box, opacity, and letter spacing.
- Passed bounded caption motion settings through the render API into ASS generation so selected effects are baked into server-rendered MP4 captions.
- Existing caption appearance and static motion remain the defaults; new motion/effects are opt-in.
- Android release signing and release artifacts were not changed.
- CI verification: GitHub Actions run 43430103177 passed Python syntax, caption-motion helper tests, TypeScript/Vite frontend build, Capacitor sync, Gradle debug APK build, and artifact upload. Device runtime validation remains pending.
- Test APK commit: 10e0f302fab5cca359a8b48bd4f209d9e7698266; artifact ID: 14039896103; APK SHA-256: 8651b90839d942dede7a105325114c1034949741206fd1fbfbfcb67b9181f568.
