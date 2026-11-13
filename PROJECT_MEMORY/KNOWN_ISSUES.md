# Known Issues / Audit Items

## Pending verification
1. First-person title sanitizer regex: RESOLVED LOCALLY on 2026-11-12. Targeted tests and syntax checks passed; live backend/device validation remains pending.
2. Fallback title_suggestion duplication: RESOLVED LOCALLY on 2026-11-12. Alternative wording now comes from another transcript phrase when available; otherwise it remains empty so the frontend can fall back to the main title.
3. Main repository local modifications have not been committed or fully regression-tested.
4. Android native DownloadManager changes need explicit device/runtime validation.
5. Full API contracts and architecture maps remain unaudited.

Do not silently fix these items. Inspect, reproduce, assess impact and record the result first.


## Resolved locally — 2026-11-12

### First-person title sanitizer regex escaping
- Location: `backend/utils/text.py`, `sanitize_first_person_title()`.
- Cause: double-escaped regex tokens prevented intended matching and capture-group replacement.
- Fix: corrected regex escaping and adjusted the "What I think about..." rewrite to avoid duplicate wording.
- Verification: 13/13 targeted cases passed; Python syntax compilation and `git diff --check` passed.
- Status: RESOLVED IN LOCAL WORKTREE; not yet committed or validated through live backend/device execution.
- Backup retained: `backend/utils/text.py.before_sanitizer_regex_fix_20261112_162549`.


### Fallback title suggestion duplication
- Location: `backend/routers/analyze.py`, transcript fallback clip construction.
- Cause: `title_suggestion` was assigned the same value as `title`.
- Fix: derive an alternative from a later sentence or a phrase after punctuation in the first sentence. If no distinct phrase with at least two words exists, keep the suggestion empty.
- Verification: two-sentence, comma-separated phrase, and short-transcript cases behaved as expected; `py_compile` and `git diff --check` passed.
- Status: RESOLVED IN LOCAL WORKTREE; no live backend/device test or APK build performed.
- Backup retained: `backend/routers/analyze.py.before_distinct_fallback_titles_20261112_163408`.


## 2026-11-13 — Dependency audit follow-up
- GitHub Actions `npm ci` reports 19 vulnerabilities in the installed 266-package dependency tree: 11 moderate, 7 high, and 1 critical.
- This is a dependency-tree summary only; affected package paths and exploitability have not yet been triaged.
- No `npm audit fix` or forced dependency upgrades were applied during the Studio implementation to avoid introducing untested breaking changes.
- Follow-up: inspect `npm audit --json`, identify direct/transitive paths, and update only with regression/build verification.
