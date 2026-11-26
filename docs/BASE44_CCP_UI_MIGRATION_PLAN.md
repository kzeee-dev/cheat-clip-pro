# Base44 → Cheat Clip Pro UI Migration Plan

## Status

- Reference assets are preserved in `base44-ui-assets/` on branch `base44-ui-assets-20261126`.
- This plan branch is isolated: `base44-ccp-redesign-20261126`.
- No CCP runtime, backend, AI provider, render pipeline, package configuration, or production source has been changed by this planning commit.
- Base44 export is a compiled frontend bundle, not its original editable React/TypeScript source. Treat it as a visual/interaction reference, not as an application to mount inside CCP.

## Product rule

Cheat Clip Pro remains the product and functional foundation. Rebuild its presentation using the Base44 visual direction while preserving CCP behavior and API contracts. Do not import Base44 mock services, sample data, fake progress, Base44 authentication, or placeholder AI responses.

## Verified CCP foundations

The inspected CCP baseline already contains:

- `src/App.tsx`: primary workflow, source selection, analysis state, network/backend monitoring, result and clip presentation, provider settings, and API calls.
- `src/components/ClipStudioSection.tsx`: live clip preview and editing controls, composition settings, face tracking, facecam layouts, subtitle controls, and render launch/progress integration.
- `src/components/HeatmapTimeline.tsx`: seekable timeline/heatmap interaction.
- `src/types.ts`: typed clip, transcript, aspect ratio, background, facecam, and render settings contracts.
- `src/utils/api.ts`: resilient API client and Android native loopback routing to `http://localhost:8000`.
- Modular CSS under `src/styles/`, including tokens, shared components, source input, clip results, and studio styles.

These are the behavior-owning parts and must remain authoritative.

## Base44 visual reference map

| Base44 reference | CCP destination / strategy |
|---|---|
| Dashboard shell, dark surfaces, purple accents, typography | Add a new app-shell layer around the existing CCP workflow; preserve mobile safe-area behavior |
| AI Clipper / source form | Restyle CCP source input and analysis entry points; keep existing YouTube, upload, cookie, and backend calls |
| My Clips / ClipCard | Restyle existing `ViralClip` result cards; retain actual score, transcript, timestamps, and selection behavior |
| Clip Studio | Restyle `ClipStudioSection`; retain preview, trim, composition, subtitle, tracking, and render callbacks |
| Subtitles | Present existing transcript/subtitle controls; do not replace the Whisper pipeline |
| Render Queue | Bind the real CCP batch render progress/events; never use simulated timers |
| Results | Bind actual saved/exported outputs; never display fixture files |
| Settings | Restyle existing provider and app settings; keep CCP Gemini/OpenRouter configuration and local backend settings |
| Login/Register/MFA | Exclude Base44-specific auth unless CCP itself has a matching requirement |

## Visual tokens to translate

Base44 direction observed in the compiled CSS/JS:
- deep charcoal / near-black surfaces;
- restrained purple/violet primary accents;
- rounded cards and controls;
- compact dashboard cards, clear status pills, and Lucide-style icons;
- readable sans-serif typography and clear heading hierarchy.

CCP currently has a distinct cyberpunk/brutalist design system (neon magenta, square corners, JetBrains Mono headings, Inter body text). Migration should replace visual treatment deliberately, not stack competing global CSS overrides. Define the new tokens centrally and migrate component classes in small batches.

## Implementation sequence

### Phase 0 — Protect and baseline
1. Keep `~/cheat-clip-pro` working tree and all pre-existing local modifications/backups untouched.
2. Work on a dedicated feature branch created from the user's chosen current CCP baseline.
3. Record current build/lint results and capture the existing Android UI before styling changes.
4. Do not reset, stash, clean, rebase, merge, or change signing/APK artifacts without explicit approval.

### Phase 1 — Shell and design tokens
1. Add a dedicated app-shell component and navigation presentation.
2. Keep the existing workflow state and callbacks in `App.tsx`; shell navigation only changes which existing CCP section is visible.
3. Introduce Base44-inspired design tokens in the modular stylesheet.
4. Verify desktop and Android mobile safe areas, scrolling, keyboard, and back navigation.

### Phase 2 — Core CCP screens
1. Source / AI Clipper: existing YouTube URL, upload, cookie and analysis flow.
2. Results / My Clips: existing clips, scores, timestamps, transcript and selection.
3. Clip Studio: existing live preview and settings.
4. Subtitles: existing Whisper-derived transcript and subtitle rendering.
5. Queue / Results: existing real batch events, saved render paths and export actions.
6. Settings: existing Gemini/OpenRouter and CCP preferences.

### Phase 3 — Verification
- `npm run build`
- `npm run lint`
- Exercise YouTube and upload analysis against the existing backend.
- Confirm Gemini Visual Analysis and Torch/Whisper behavior remains unchanged.
- Exercise Clip Studio preview, aspect ratios, black/blur backgrounds, face tracking, streamer layouts, facecam positions, subtitles, and trim.
- Start/cancel/retry batch render; verify real queue progress and exported MP4.
- Build/install Android APK only after web checks pass; verify safe areas and existing backend connection on device.

## Non-goals

- Do not replace CCP with the Base44 export.
- Do not create a second product or revive Clipper Ultra Infinity.
- Do not replace Torch/Whisper/Gemini/YouTube/FFmpeg with mock implementations.
- Do not change backend routes or data contracts merely to match Base44 labels.
- Do not merge this branch into the default branch until user review and device verification.

## Next implementation unit

Start with the app shell and design tokens only. Before touching the large `App.tsx`, identify its existing header and workflow navigation boundaries and extract presentation incrementally while keeping all state, effects, and service calls in place.
