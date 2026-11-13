import React, { useMemo, useState } from 'react';
import { ChevronDown, ChevronUp, Plus, Sparkles, X } from 'lucide-react';
import type { CaptionMotionSettings, CaptionMotionPreset, TranscriptLine, ViralClip } from '../types';
import { suggestCaptionHighlights } from '../utils/captionMotion';
import './CaptionMotionPanel.css';

interface Props {
  value: CaptionMotionSettings;
  onChange: (next: CaptionMotionSettings) => void;
  clips: ViralClip[];
  transcript: TranscriptLine[];
}

const PRESETS: Array<{ id: CaptionMotionPreset; name: string; description: string }> = [
  { id: 'none', name: 'Static', description: 'Tanpa animasi' },
  { id: 'cinematic', name: 'Cinematic', description: 'Fade lembut dan elegan' },
  { id: 'punch_impact', name: 'Punch Impact', description: 'Pop tegas untuk hook' },
  { id: 'smooth_pop', name: 'Smooth Pop', description: 'Muncul halus dan ringan' },
  { id: 'kinetic_flow', name: 'Kinetic Flow', description: 'Gerak tipografi dinamis' },
  { id: 'bounce_pro', name: 'Bounce Pro', description: 'Bounce pendek terkontrol' },
  { id: 'glitch_pro', name: 'Glitch Pro', description: 'Blur cepat dan subtle' },
  { id: 'type_reveal', name: 'Type Reveal', description: 'Reveal per kata' },
  { id: 'slide_motion', name: 'Slide Motion', description: 'Transisi masuk halus' },
  { id: 'focus_zoom', name: 'Focus Zoom', description: 'Fokus dari blur ke tajam' },
];

const COLORS = [
  { value: '#FFB800', label: 'Gold' },
  { value: '#FFE600', label: 'Yellow' },
  { value: '#00E5FF', label: 'Cyan' },
  { value: '#FF4D6D', label: 'Coral' },
  { value: '#B8FF45', label: 'Lime' },
  { value: '#C084FC', label: 'Violet' },
];

export const CaptionMotionPanel: React.FC<Props> = ({ value, onChange, clips, transcript }) => {
  const [expanded, setExpanded] = useState(true);
  const [draftTerm, setDraftTerm] = useState('');
  const suggestions = useMemo(() => suggestCaptionHighlights(clips, transcript), [clips, transcript]);
  const update = (patch: Partial<CaptionMotionSettings>) => onChange({ ...value, ...patch });
  const addTerm = (term: string) => {
    const clean = term.trim().replace(/[,;]+$/g, '');
    if (!clean || value.manualHighlightTerms.some(item => item.toLowerCase() === clean.toLowerCase())) return;
    update({ manualHighlightTerms: [...value.manualHighlightTerms, clean].slice(0, 30) });
    setDraftTerm('');
  };
  const removeTerm = (term: string) => update({ manualHighlightTerms: value.manualHighlightTerms.filter(item => item !== term) });

  return (
    <section className="caption-motion-panel">
      <button type="button" className="cmp-heading" onClick={() => setExpanded(open => !open)} aria-expanded={expanded}>
        <span className="cmp-heading-mark"><Sparkles size={17} /></span>
        <span className="cmp-heading-copy">
          <strong>CAPTION MOTION LAB</strong>
          <small>Smart highlight · Motion presets · Text effects</small>
        </span>
        <span className="cmp-heading-status">RENDER READY</span>
        {expanded ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
      </button>

      {expanded && (
        <div className="cmp-body">
          <div className="cmp-highlight-card">
            <div className="cmp-card-heading">
              <div>
                <strong>Smart Highlight Keywords</strong>
                <p>Kata saran berasal dari AI key quotes dan konteks transkrip. Ini hanya penekanan visual; teks asli tidak diubah.</p>
              </div>
              <label className="cmp-switch">
                <input type="checkbox" checked={value.autoHighlight} onChange={e => update({ autoHighlight: e.target.checked })} />
                <span>{value.autoHighlight ? 'AUTO ON' : 'AUTO OFF'}</span>
              </label>
            </div>
            <div className="cmp-suggestion-list">
              {suggestions.length ? suggestions.map(term => (
                <button key={term} type="button" className={value.autoHighlight ? 'cmp-chip active' : 'cmp-chip'} onClick={() => addTerm(term)} title="Tambah sebagai highlight manual">
                  {term}<Plus size={12} />
                </button>
              )) : <span className="cmp-empty">Belum ada kata yang cukup kuat dari clip terpilih.</span>}
            </div>
            <div className="cmp-manual-row">
              <input value={draftTerm} onChange={e => setDraftTerm(e.target.value)} onKeyDown={e => { if (e.key === 'Enter') { e.preventDefault(); addTerm(draftTerm); } }} placeholder="Tambah kata manual, lalu Enter…" aria-label="Kata highlight manual" />
              <button type="button" onClick={() => addTerm(draftTerm)} disabled={!draftTerm.trim()}><Plus size={15} /> Tambah</button>
            </div>
            {value.manualHighlightTerms.length > 0 && (
              <div className="cmp-suggestion-list cmp-manual-chips">
                {value.manualHighlightTerms.map(term => (
                  <span className="cmp-chip manual" key={term}>{term}<button type="button" onClick={() => removeTerm(term)} aria-label="Hapus kata highlight"><X size={12} /></button></span>
                ))}
              </div>
            )}
            <label className="cmp-color-field">
              <span>Warna highlight kata</span>
              <select value={value.highlightColor} onChange={e => update({ highlightColor: e.target.value })}>
                {COLORS.map(color => <option value={color.value} key={color.value}>{color.label}</option>)}
              </select>
            </label>
          </div>

          <div className="cmp-section">
            <div className="cmp-section-title"><strong>Professional Motion Presets</strong><span>10 gaya</span></div>
            <div className="cmp-preset-grid">
              {PRESETS.map(preset => (
                <button type="button" key={preset.id} className={value.motionPreset === preset.id ? 'cmp-preset active' : 'cmp-preset'} onClick={() => update({ motionPreset: preset.id })}>
                  <strong>{preset.name}</strong><small>{preset.description}</small>
                </button>
              ))}
            </div>
            <div className="cmp-range-grid">
              <label className="cmp-range"><span>Intensitas <b>{value.motionIntensity}%</b></span><input type="range" min="0" max="100" value={value.motionIntensity} onChange={e => update({ motionIntensity: Number(e.target.value) })} /></label>
              <label className="cmp-range"><span>Kecepatan <b>{value.motionSpeed.toFixed(1)}×</b></span><input type="range" min="0.5" max="2" step="0.1" value={value.motionSpeed} onChange={e => update({ motionSpeed: Number(e.target.value) })} /></label>
            </div>
          </div>

          <div className="cmp-section">
            <div className="cmp-section-title"><strong>Advanced Text Effects</strong><span>Render controls</span></div>
            <div className="cmp-range-grid">
              <label className="cmp-range"><span>Stroke / Outline <b>{value.outlineWidth.toFixed(1)}</b></span><input type="range" min="0" max="9" step="0.5" value={value.outlineWidth} onChange={e => update({ outlineWidth: Number(e.target.value) })} /></label>
              <label className="cmp-range"><span>Shadow depth <b>{value.shadowDepth.toFixed(1)}</b></span><input type="range" min="0" max="8" step="0.5" value={value.shadowDepth} onChange={e => update({ shadowDepth: Number(e.target.value) })} /></label>
              <label className="cmp-range"><span>Neon glow <b>{value.glowStrength.toFixed(1)}</b></span><input type="range" min="0" max="5" step="0.5" value={value.glowStrength} onChange={e => update({ glowStrength: Number(e.target.value) })} /></label>
              <label className="cmp-range"><span>Letter spacing <b>{value.letterSpacing.toFixed(1)}</b></span><input type="range" min="-1" max="5" step="0.5" value={value.letterSpacing} onChange={e => update({ letterSpacing: Number(e.target.value) })} /></label>
              <label className="cmp-range"><span>Box opacity <b>{value.backgroundOpacity}%</b></span><input type="range" min="10" max="100" step="5" value={value.backgroundOpacity} onChange={e => update({ backgroundOpacity: Number(e.target.value) })} /></label>
            </div>
            <label className="cmp-box-toggle"><input type="checkbox" checked={value.backgroundBox} onChange={e => update({ backgroundBox: e.target.checked })} /><span>Caption background box</span></label>
          </div>

          <div className="cmp-preview">
            <span className="cmp-preview-label">STYLE PREVIEW</span>
            <div className="cmp-preview-canvas">
              <span style={{
                color: '#fff',
                WebkitTextStroke: (value.outlineWidth > 0 ? Math.min(value.outlineWidth, 3) : 0) + 'px #101018',
                textShadow: value.glowStrength > 0 ? '0 0 ' + (value.glowStrength * 4) + 'px ' + value.highlightColor : '0 ' + (value.shadowDepth / 2) + 'px ' + value.shadowDepth + 'px #000',
                letterSpacing: value.letterSpacing + 'px',
                background: value.backgroundBox ? 'rgba(0,0,0,' + (value.backgroundOpacity / 100) + ')' : 'transparent',
                padding: value.backgroundBox ? '8px 12px' : 0,
                borderRadius: 6,
              }}>INI MOMEN <b style={{ color: value.highlightColor }}>PALING PENTING</b></span>
            </div>
            <small>Preview kontrol. Hasil akhir diproses saat render FFmpeg.</small>
          </div>
        </div>
      )}
    </section>
  );
};
