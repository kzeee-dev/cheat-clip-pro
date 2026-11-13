# Regression Checklist

Run relevant checks before and after every change.

## Analysis
- [ ] Transcript analysis works.
- [ ] Visual-only analysis works.
- [ ] Subtitle ON works.
- [ ] Subtitle OFF skips transcription as intended.
- [ ] Subtitle setting persists.
- [ ] Gemini visual analysis and authentic frames work.
- [ ] OpenRouter fallback works.
- [ ] Titles, captions and hashtags remain grounded in source content.
- [ ] Empty transcript segments do not create invented clips.

## Rendering
- [ ] Single render works.
- [ ] Batch render works.
- [ ] Merged render works.
- [ ] Live terminal and progress update.
- [ ] Audio remains synchronized.
- [ ] Silent segments are handled.
- [ ] CPU fallback works.
- [ ] Smart Face Tracking remains functional.

## Downloads and media
- [ ] YouTube metadata retrieval works.
- [ ] Audio download and validation work.
- [ ] Authentic frame extraction works.
- [ ] Cookie and proxy fallback work.
- [ ] Preview and MP4/ZIP/PKG downloads work.
- [ ] Download status and network-stall handling work.

## Android
- [ ] WebView integration works.
- [ ] Native DownloadManager works.
- [ ] Notification permission flow works on Android 13+.
- [ ] Download continues when notification permission is denied.
- [ ] Download completion/status handling works.

## Release safety
- [ ] Existing release APK preserved.
- [ ] Release signing configuration unchanged.
- [ ] Debug build does not overwrite release artifact.
- [ ] CI result and artifact recorded.

Do not mark a checkbox complete without an actual test result.

## Clip Studio editor
- [ ] Studio opens and retains existing settings on Android.
- [ ] Mobile portrait layout keeps preview, controls and render action usable.
- [ ] Compact landscape layout keeps preview and controls visible without horizontal overflow.
- [ ] Timeline video track and playhead follow playback and scrubbing.
- [ ] Tapping transcript caption markers seeks to the corresponding timestamp.
- [ ] Empty transcript state displays safely without breaking preview.
- [ ] Orientation change preserves selected clip, playback position and editor settings.
