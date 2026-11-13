# Cheat Clip Pro — Project History

## Project Preservation Policy
- Existing completed features must not be removed or silently changed.
- No unrelated behavior changes.
- Never overwrite uncommitted work or backup files.
- Never reset, stash, or destructively switch branches.
- Never alter main or release signing configuration without explicit permission.
- Every change must record its reason, affected files, feature impact, tests, commit, and build status.
- Audit regression risks before modifying existing functionality.
- Distinguish confirmed tests from untested assumptions.

## Confirmed Baseline — 2026-11-12
- Branch: fix/media-source-resilience
- Commit: c48eb092e4c0e1ef41f5cc96cba5a94e1ea2a6f8
- GitHub Actions: Build Android APK #142
- CI build status: SUCCESS
- Debug APK artifact: Cheat-Clip-Pro-Debug-APK
- User acceptance: user declared this build perfect.
- Device installation/runtime validation: NOT YET CONFIRMED.
- Existing release APK and signing configuration must remain untouched.

## Repository Separation
Main working repository:
- Path: ~/cheat-clip-pro
- Branch: integrate/visual-analysis-android
- Commit: 2abd079
- Has uncommitted modifications and backup files. Preserve all.

Media test worktree:
- Path: ~/ccp-media-test-20261112
- Branch: fix/media-source-resilience
- Commit: c48eb09
- Contains isolated media test output. Preserve it.

## Local Work Pending Commit
The main repository has six modified tracked files and multiple untracked backup files.
These changes are separate from the c48eb09 media-fix baseline.
Do not merge, commit, discard, or copy them without an explicit review.

## Documentation Rule
Update this history and SESSION_LOG.md after every meaningful work session.
