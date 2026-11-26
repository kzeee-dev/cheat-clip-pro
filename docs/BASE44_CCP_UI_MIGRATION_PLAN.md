# Base44 → CCP UI Redesign (Latest CCP Baseline)

## Branch safety
- Implementation branch: `base44-ccp-redesign-latest-20261126`
- Source baseline: `update/live-render-terminal`
- Base44 reference assets remain isolated on `base44-ui-assets-20261126`.
- Do not merge the older snapshot-based Base44 assets branch into this branch.
- No runtime files have been modified in this branch yet.

## Product rule
Cheat Clip Pro remains the working product. Base44 is a visual reference only. Preserve the current CCP source, backend contracts, YouTube workflow, Torch/Whisper, Gemini Visual Analysis, clip selection, subtitles, Clip Studio, FFmpeg rendering, and queue behavior.

## Confirmed current CCP foundations
- `src/App.tsx`: existing source/analysis/results workflow, provider settings, API calls and workflow navigation.
- `src/components/ClipStudioSection.tsx`: preview/editor controls, composition, face tracking, facecam, subtitles, and actual render callbacks.
- `src/components/HeatmapTimeline.tsx`: real seekable timeline and heatmap.
- `src/types.ts`: current clip/transcript/render contracts.
- `src/utils/api.ts`: resilient API client; Android requests route to local backend at `http://localhost:8000`.
- `src/styles/*.css`: modular existing CCP design system.

## Base44 visual mapping
| Base44 reference | CCP implementation target |
|---|---|
| Dashboard shell and navigation | New presentation shell around existing CCP workflow state |
| AI Clipper | Restyle existing source input; preserve YouTube/upload/cookie/backend calls |
| My Clips / ClipCard | Restyle real CCP clip cards and scores |
| Clip Studio | Restyle existing ClipStudioSection; preserve every editor callback |
| Subtitles | Present existing Whisper transcript/subtitle controls |
| Render Queue | Display actual CCP batch progress/events only |
| Results | Display actual saved/exported files only |
| Settings | Restyle existing CCP provider and app settings |
| Base44 Login/Register/MFA | Exclude Base44-specific authentication |

## Visual direction
Use Base44's near-black surfaces, restrained violet/purple accent, rounded cards, compact status pills, clear hierarchy, and Lucide-style iconography. Replace CCP's existing cyberpunk/magenta styling deliberately through centralized tokens and component-level CSS migration. Avoid stacking broad global overrides.

## Safe implementation order
1. Capture baseline build/lint and current Android UI.
2. Identify exact existing header and workflow navigation boundaries in the latest `src/App.tsx`.
3. Add an isolated shell/presentation component without moving CCP state, effects, API calls, or render callbacks.
4. Add centralized visual tokens and responsive shell styles.
5. Restyle existing source/result/studio/queue/settings views in small batches.
6. Run build/lint and verify YouTube, upload, AI, subtitles, preview, render, queue, export, Android safe areas, and backend connectivity.

## Guardrails
- No Base44 mock services, sample data, simulated progress, or fake AI responses.
- No replacement of CCP backend routes or data contracts for visual parity.
- No package/dependency changes unless a concrete missing dependency is demonstrated.
- No changes to signing/APK artifacts, local runtime services, or pre-existing local working-tree files.
- No reset, clean, stash, rebase, force-push, or merge to the default branch.
- Review and device verification are required before any merge.

## First implementation unit
Inspect the latest `src/App.tsx` header/navigation and CSS import boundaries, then add the shell as a presentation-only layer. Do not rewrite the monolithic App component or refactor business logic as part of the first UI pass.
