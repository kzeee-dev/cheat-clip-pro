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


## Auto Clipper Studio Caption Motion Lab — device validation
- [ ] Install the debug-suffix APK alongside the production app; confirm the release app remains installed and launches.
- [ ] Launch the test app and confirm backend connectivity and existing project features.
- [ ] Render a short clip with subtitles ON and OFF; verify subtitle toggle behavior remains unchanged.
- [ ] Render with each motion preset; verify no flicker, clipping, overlap, or vertical position jumps.
- [ ] Test smart keyword suggestions and manual overrides; confirm only visual emphasis changes and transcript text remains identical.
- [ ] Test highlight colors, custom stroke/shadow overrides, glow, background box opacity, and letter spacing.
- [ ] Verify existing caption style presets retain their default stroke/shadow when custom overrides are disabled.
- [ ] Rotate portrait to landscape and back while editing; verify playhead, selected clip, and caption settings persist.
- [ ] Test on a small phone viewport and landscape viewport; verify controls remain reachable above system bars and keyboard.
