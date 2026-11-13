import React, { useMemo, useState } from 'react';
import type { ProCaptionSettings, TranscriptLine } from '../types';

export const DEFAULT_PRO_CAPTION_SETTINGS: ProCaptionSettings = {
  aiHighlightEnabled: false,
  aiHighlightIntensity: 72,
  aiHighlightColor: '#FFE600',
  aiHighlightManualWords: '',
  aiHighlightExcludedWords: '',
  motionPreset: 'none',
  motionSpeed: 1,
  motionDurationMs: 280,
  motionIntensity: 72,
  motionDelayMs: 0,
  motionScope: 'word',
  motionEasing: 'ease-out',
  textOutline: 4.8,
  textShadow: 2,
  textGlow: 0,
  textGradient: false,
  textGradientStart: '#FFE600',
  textGradientEnd: '#00E5FF',
  textBackground: false,
  textBackgroundOpacity: 58,
  textLetterSpacing: 0,
  textWeight: 'bold',
  textScale: 100,
};

const EMOTIONAL_TERMS = new Set([
  'ternyata','rahasia','akhirnya','terbukti','mengejutkan','menakjubkan','gila','parah','hebat','luar','biasa',
  'penting','bahaya','awas','jangan','wajib','gratis','mudah','susah','terbaik','terburuk','berhasil','sukses',
  'gagal','menang','kalah','viral','serius','percaya','mustahil','wow','kaget','takut','sedih','senang','marah',
  'amazing','secret','shocking','surprising','unbelievable','important','danger','warning','free','easy','best',
  'worst','success','fail','win','lose','never','always','finally','revealed','proven','insane','crazy','love',
  'hate','fear','beautiful','powerful','mistake','truth','hack','exclusive','urgent','money','million',
]);

const STOP_WORDS = new Set([
  'yang','dan','atau','di','ke','dari','ini','itu','untuk','dengan','pada','adalah','jadi','akan','bisa',
  'ada','saya','aku','kamu','dia','mereka','kita','kami','anda','dalam','karena','kalau','jika','seperti',
  'lebih','sangat','sudah','belum','tidak','bukan','juga','pun','nya','lah','the','and','or','to','of','in',
  'on','for','with','is','are','was','were','be','been','being','this','that','these','those','it','its',
  'you','your','we','they','he','she','i','a','an','as','at','by','from','but','so','if','then','than',
]);

const normalize = (word: string) => word.toLocaleLowerCase().replace(/^[^\p{L}\p{N}]+|[^\p{L}\p{N}]+$/gu, '');

export function getAiHighlightWords(transcript: TranscriptLine[], settings: ProCaptionSettings): string[] {
  if (!settings.aiHighlightEnabled) return [];
  const scores = new Map<string, number>();
  for (const line of transcript || []) {
    const engagement = Math.max(0, Math.min(1, Number(line.engagement || 0)));
    const tokens = String(line.text || '').match(/[\p{L}\p{N}']+/gu) || [];
    for (const raw of tokens) {
      const word = normalize(raw);
      if (word.length < 4 || STOP_WORDS.has(word)) continue;
      const lexical = EMOTIONAL_TERMS.has(word) ? 3.2 : 0;
      const lengthSignal = Math.min(0.7, Math.max(0, word.length - 5) * 0.12);
      const score = lexical + lengthSignal + engagement * 0.8;
      if (score > 0) scores.set(word, (scores.get(word) || 0) + score);
    }
  }
  const excluded = new Set((settings.aiHighlightExcludedWords || '').split(/[;,\n]+/).map(normalize).filter(Boolean));
  const manual = (settings.aiHighlightManualWords || '').split(/[;,\n]+/).map(normalize).filter(Boolean);
  const threshold = 1.15 - (Math.max(0, Math.min(100, settings.aiHighlightIntensity)) / 100) * 0.75;
  const maxAuto = Math.max(3, Math.min(12, Math.round(3 + settings.aiHighlightIntensity / 12)));
  const detected = [...scores.entries()]
    .filter(([word, score]) => score >= threshold && !excluded.has(word))
    .sort((a, b) => b[1] - a[1])
    .slice(0, maxAuto)
    .map(([word]) => word);
  return [...new Set([...detected, ...manual.filter(word => !excluded.has(word))])];
}

const MOTION_PRESETS: Array<{ id: ProCaptionSettings['motionPreset']; name: string; detail: string }> = [
  { id: 'none', name: 'None', detail: 'Original stable karaoke captions' },
  { id: 'cinematic', name: 'Cinematic', detail: 'Soft fade and restrained scale' },
  { id: 'punch_impact', name: 'Punch Impact', detail: 'Fast impact pop' },
  { id: 'smooth_pop', name: 'Smooth Pop', detail: 'Smooth scale-in' },
  { id: 'kinetic_flow', name: 'Kinetic Flow', detail: 'Subtle kinetic rotation' },
  { id: 'bounce_pro', name: 'Bounce Pro', detail: 'Elastic bounce settle' },
  { id: 'glitch_pro', name: 'Glitch Pro', detail: 'Sharp digital distortion' },
  { id: 'type_reveal', name: 'Type Reveal', detail: 'Fade-on reveal' },
  { id: 'slide_motion', name: 'Slide Motion', detail: 'Horizontal reveal feel' },
  { id: 'focus_zoom', name: 'Focus Zoom', detail: 'Blur-to-focus zoom' },
];

interface Props {
  value: ProCaptionSettings;
  transcript: TranscriptLine[];
  onChange: (next: ProCaptionSettings) => void;
}

const SAVED_STYLES_KEY = 'ccp_pro_caption_saved_styles';

export const ProCaptionControls: React.FC<Props> = ({ value, transcript, onChange }) => {
  const detectedWords = useMemo(() => getAiHighlightWords(transcript, value), [transcript, value]);
  const [styleName, setStyleName] = useState('My Pro Style');
  const [savedStyles, setSavedStyles] = useState<Record<string, Partial<ProCaptionSettings>>>(() => {
    try { return JSON.parse(localStorage.getItem(SAVED_STYLES_KEY) || '{}'); } catch { return {}; }
  });
  const update = <K extends keyof ProCaptionSettings>(key: K, next: ProCaptionSettings[K]) => onChange({ ...value, [key]: next });
  const saveStyle = () => {
    const name = styleName.trim();
    if (!name) return;
    const next = { ...savedStyles, [name]: {
      textOutline: value.textOutline, textShadow: value.textShadow, textGlow: value.textGlow,
      textGradient: value.textGradient, textGradientStart: value.textGradientStart,
      textGradientEnd: value.textGradientEnd, textBackground: value.textBackground,
      textBackgroundOpacity: value.textBackgroundOpacity, textLetterSpacing: value.textLetterSpacing,
      textWeight: value.textWeight, textScale: value.textScale,
    }};
    setSavedStyles(next);
    try { localStorage.setItem(SAVED_STYLES_KEY, JSON.stringify(next)); } catch (error) { console.warn('Could not save caption style', error); }
  };
  const applyStyle = (name: string) => {
    const saved = savedStyles[name];
    if (saved) onChange({ ...value, ...saved });
  };
  const card: React.CSSProperties = { border: '1px solid rgba(148,163,184,.2)', borderRadius: 10, padding: 12, marginTop: 12, background: 'rgba(15,23,42,.38)' };
  const label: React.CSSProperties = { display: 'flex', justifyContent: 'space-between', gap: 10, alignItems: 'center', fontSize: '.76rem', color: 'var(--text-secondary)', marginBottom: 5 };
  const input: React.CSSProperties = { width: '100%', minWidth: 0, accentColor: 'var(--primary)' };
  const select: React.CSSProperties = { width: '100%', minWidth: 0, padding: '8px 10px', color: 'var(--text-primary)', background: 'rgba(2,6,23,.8)', border: '1px solid rgba(148,163,184,.28)', borderRadius: 7 };
  const toggle: React.CSSProperties = { display: 'flex', alignItems: 'center', gap: 8, fontSize: '.78rem', color: 'var(--text-primary)' };

  return (
    <div className="ccp-pro-caption-controls">
      <div style={{ ...card, borderColor: 'rgba(56,189,248,.38)' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 8, flexWrap: 'wrap' }}>
          <strong style={{ fontSize: '.9rem', color: 'var(--text-primary)' }}>✨ AI Highlight Keywords</strong>
          <label style={toggle}><input type="checkbox" checked={value.aiHighlightEnabled} onChange={e => update('aiHighlightEnabled', e.target.checked)} /> Enable</label>
        </div>
        <p style={{ fontSize: '.7rem', color: 'var(--text-muted)', margin: '6px 0 10px' }}>Deteksi kata emosional dan kata pemicu dari transkrip secara lokal, lalu gabungkan dengan pilihan manual.</p>
        <label style={label}><span>Detection intensity</span><strong>{value.aiHighlightIntensity}%</strong></label>
        <input style={input} type="range" min="0" max="100" value={value.aiHighlightIntensity} onChange={e => update('aiHighlightIntensity', Number(e.target.value))} />
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, marginTop: 10 }}>
          <label style={{ ...label, flexDirection: 'column', alignItems: 'flex-start' }}>Highlight color<input type="color" value={value.aiHighlightColor} onChange={e => update('aiHighlightColor', e.target.value)} /></label>
          <div style={{ fontSize: '.7rem', color: 'var(--text-muted)', alignSelf: 'end' }}>{detectedWords.length} detected / manual keywords</div>
        </div>
        <label style={{ ...label, display: 'block', marginTop: 10 }}>Manual keywords (comma separated)</label>
        <textarea value={value.aiHighlightManualWords} onChange={e => update('aiHighlightManualWords', e.target.value)} rows={2} placeholder="contoh: rahasia, ternyata, amazing" style={{ ...select, resize: 'vertical' }} />
        <label style={{ ...label, display: 'block', marginTop: 8 }}>Exclude words</label>
        <input value={value.aiHighlightExcludedWords} onChange={e => update('aiHighlightExcludedWords', e.target.value)} placeholder="kata yang tidak ingin di-highlight" style={select} />
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 5, marginTop: 9 }}>
          {detectedWords.slice(0, 12).map(word => <span key={word} style={{ padding: '3px 7px', borderRadius: 20, fontSize: '.68rem', color: value.aiHighlightColor, background: 'rgba(148,163,184,.12)', border: '1px solid rgba(148,163,184,.18)' }}>{word}</span>)}
          {!detectedWords.length && <span style={{ fontSize: '.68rem', color: 'var(--text-muted)' }}>Kata akan muncul setelah transkrip tersedia atau lu menambahkan manual keyword.</span>}
        </div>
      </div>

      <div style={card}>
        <strong style={{ fontSize: '.9rem', color: 'var(--text-primary)' }}>🎬 Professional Motion Engine</strong>
        <label style={{ ...label, display: 'block', marginTop: 10 }}>Motion preset</label>
        <select style={select} value={value.motionPreset} onChange={e => update('motionPreset', e.target.value as ProCaptionSettings['motionPreset'])}>
          {MOTION_PRESETS.map(preset => <option key={preset.id} value={preset.id}>{preset.name} — {preset.detail}</option>)}
        </select>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginTop: 12 }}>
          <div><label style={label}><span>Speed</span><strong>{value.motionSpeed.toFixed(1)}×</strong></label><input style={input} type="range" min=".5" max="2" step=".1" value={value.motionSpeed} onChange={e => update('motionSpeed', Number(e.target.value))} /></div>
          <div><label style={label}><span>Duration</span><strong>{value.motionDurationMs} ms</strong></label><input style={input} type="range" min="100" max="800" step="10" value={value.motionDurationMs} onChange={e => update('motionDurationMs', Number(e.target.value))} /></div>
          <div><label style={label}><span>Intensity</span><strong>{value.motionIntensity}%</strong></label><input style={input} type="range" min="0" max="100" value={value.motionIntensity} onChange={e => update('motionIntensity', Number(e.target.value))} /></div>
          <div><label style={label}><span>Delay</span><strong>{value.motionDelayMs} ms</strong></label><input style={input} type="range" min="0" max="500" step="10" value={value.motionDelayMs} onChange={e => update('motionDelayMs', Number(e.target.value))} /></div>
          <div><label style={{ ...label, display: 'block' }}>Scope</label><select style={select} value={value.motionScope} onChange={e => update('motionScope', e.target.value as ProCaptionSettings['motionScope'])}><option value="word">Per word</option><option value="line">Per line</option></select></div>
          <div><label style={{ ...label, display: 'block' }}>Easing</label><select style={select} value={value.motionEasing} onChange={e => update('motionEasing', e.target.value as ProCaptionSettings['motionEasing'])}><option value="linear">Linear</option><option value="ease-in">Ease In</option><option value="ease-out">Ease Out</option><option value="ease-in-out">Ease In Out</option><option value="bounce">Bounce</option></select></div>
        </div>
      </div>

      <div style={card}>
        <strong style={{ fontSize: '.9rem', color: 'var(--text-primary)' }}>Aa Advanced Text Effects</strong>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginTop: 12 }}>
          <div><label style={label}><span>Outline</span><strong>{value.textOutline.toFixed(1)}</strong></label><input style={input} type="range" min="0" max="12" step=".2" value={value.textOutline} onChange={e => update('textOutline', Number(e.target.value))} /></div>
          <div><label style={label}><span>Layered shadow</span><strong>{value.textShadow.toFixed(1)}</strong></label><input style={input} type="range" min="0" max="12" step=".2" value={value.textShadow} onChange={e => update('textShadow', Number(e.target.value))} /></div>
          <div><label style={label}><span>Glow</span><strong>{value.textGlow.toFixed(1)}</strong></label><input style={input} type="range" min="0" max="8" step=".2" value={value.textGlow} onChange={e => update('textGlow', Number(e.target.value))} /></div>
          <div><label style={label}><span>Scale</span><strong>{value.textScale}%</strong></label><input style={input} type="range" min="70" max="140" step="1" value={value.textScale} onChange={e => update('textScale', Number(e.target.value))} /></div>
          <div><label style={label}><span>Letter spacing</span><strong>{value.textLetterSpacing.toFixed(1)}</strong></label><input style={input} type="range" min="-2" max="12" step=".2" value={value.textLetterSpacing} onChange={e => update('textLetterSpacing', Number(e.target.value))} /></div>
          <div><label style={{ ...label, display: 'block' }}>Font weight</label><select style={select} value={value.textWeight} onChange={e => update('textWeight', e.target.value as ProCaptionSettings['textWeight'])}><option value="normal">Normal</option><option value="bold">Bold</option><option value="black">Black</option></select></div>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, marginTop: 12 }}>
          <label style={toggle}><input type="checkbox" checked={value.textGradient} onChange={e => update('textGradient', e.target.checked)} /> Gradient highlight</label>
          <label style={toggle}><input type="checkbox" checked={value.textBackground} onChange={e => update('textBackground', e.target.checked)} /> Background box</label>
          <label style={{ ...label, flexDirection: 'column', alignItems: 'flex-start' }}>Gradient start<input type="color" value={value.textGradientStart} onChange={e => update('textGradientStart', e.target.value)} /></label>
          <label style={{ ...label, flexDirection: 'column', alignItems: 'flex-start' }}>Gradient end<input type="color" value={value.textGradientEnd} onChange={e => update('textGradientEnd', e.target.value)} /></label>
        </div>
        {value.textBackground && <div style={{ marginTop: 10 }}><label style={label}><span>Background opacity</span><strong>{value.textBackgroundOpacity}%</strong></label><input style={input} type="range" min="10" max="100" value={value.textBackgroundOpacity} onChange={e => update('textBackgroundOpacity', Number(e.target.value))} /></div>}
        <div style={{ display: 'flex', gap: 7, marginTop: 13, flexWrap: 'wrap' }}>
          <input value={styleName} onChange={e => setStyleName(e.target.value)} aria-label="Saved style name" style={{ ...select, flex: '1 1 120px' }} />
          <button type="button" onClick={saveStyle} style={{ padding: '8px 11px', borderRadius: 7, border: '1px solid rgba(56,189,248,.45)', background: 'rgba(56,189,248,.12)', color: 'var(--text-primary)', fontWeight: 700 }}>Save style</button>
          <select aria-label="Load saved style" defaultValue="" onChange={e => applyStyle(e.target.value)} style={{ ...select, flex: '1 1 120px' }}>
            <option value="" disabled>Load saved style…</option>
            {Object.keys(savedStyles).map(name => <option key={name} value={name}>{name}</option>)}
          </select>
        </div>
      </div>
    </div>
  );
};
