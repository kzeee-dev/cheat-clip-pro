# Cheat Clip Pro — Hybrid Pro Caption Studio

Branch: `feature/hybrid-pro-studio-2026-11-13`  
Base: `snapshot/phone-project-2026-11-13` at `b2ea02e379748a1ab91bb9a07f31e7f86f9d72b9`

## Scope

This implementation adds three connected Studio capabilities while preserving the existing caption, subtitle toggle, single/batch/merged render paths, and the existing release configuration.

### AI Highlight Keywords

- Transcript-based local scoring looks for emotional and high-signal terms in Indonesian and English.
- Detection intensity adjusts the score threshold and number of suggested words.
- Users can add manual keywords and exclude unwanted words.
- The selected color and intensity are sent with the render request and applied to matching word-level ASS events.
- The local detector is a deterministic transcript heuristic; it does not call a remote LLM or require a Gemini key. This keeps it usable when Gemini is not configured. It should be described as local AI-assisted/automatic keyword scoring, not as a Gemini inference.

### Professional Motion Engine

Presets: Cinematic, Punch Impact, Smooth Pop, Kinetic Flow, Bounce Pro, Glitch Pro, Type Reveal, Slide Motion, and Focus Zoom.

Controls: speed, duration, intensity, delay, easing, and per-word/per-line scope. The preview animates the active word; the server ASS renderer burns the corresponding motion tags into the output.

### Advanced Text Effects

- Outline and shadow overrides; unset values preserve the legacy caption-style-specific outline/shadow.
- Glow, gradient highlight colors, opaque/translucent background box, letter spacing, font weight, and scale.
- Save and reload named text-effect styles in local browser storage.

## Rendering integration

- Studio preferences persist the new controls under the existing Studio preferences key.
- The settings are sent through `/api/render-batch` as `pro_caption`.
- The backend schema accepts the optional object without breaking older clients.
- Both separate and merged rendering pass the settings to `generate_ass_file`.
- If a Pro caption feature is actually changed from its legacy default, the app routes that render through the backend because the browser WASM/WebCodecs renderers do not burn these ASS subtitle effects. Ordinary jobs retain the existing client-render path.

## Validation still required

- GitHub Actions Android debug build must pass (Python compileall, TypeScript/Vite build, Capacitor sync, Gradle assembleDebug).
- Verify the new panel on a real Android device.
- Render one short test clip with AI highlights, one with each motion preset, and one with text effects; inspect timing, readability, and output file playback.
- Verify subtitle ON/OFF, existing caption styles, single render, batch render, merged render, download, and live render progress still work.
- Verify a render with all Pro controls left untouched retains the old renderer path and legacy style defaults.

## Safety

This branch is isolated from `snapshot/phone-project-2026-11-13`, the successful build #142 baseline branch/worktree, and the existing release APK/signing configuration. Do not merge or replace the release artifact until the build and device tests pass.
