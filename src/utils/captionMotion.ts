import type { CaptionMotionSettings, TranscriptLine, ViralClip } from '../types';

export const DEFAULT_CAPTION_MOTION_SETTINGS: CaptionMotionSettings = {
  motionPreset: 'none',
  motionIntensity: 55,
  motionSpeed: 1,
  outlineWidth: 4.8,
  useCustomOutline: false,
  shadowDepth: 2,
  useCustomShadow: false,
  glowStrength: 0,
  backgroundBox: false,
  backgroundOpacity: 72,
  letterSpacing: 0,
  highlightColor: 'preset',
  autoHighlight: true,
  manualHighlightTerms: [],
};

const STOP_WORDS = new Set([
  'yang','dan','atau','untuk','dari','dengan','pada','ini','itu','ada','jadi',
  'akan','bisa','sudah','belum','kalau','karena','kita','kami','kamu','saya',
  'aku','dia','mereka','satu','lebih','juga','dalam','the','and','for','that',
  'this','with','from','have','has','you','your','are','was','were','will',
  'would','could','should','there','their','they','them','then','than','when',
  'what','why','how','about','into','just','like','really','very','some','because'
]);

const IMPACT_WORDS = new Set([
  'gila','parah','ternyata','rahasia','mustahil','berhasil','gagal','mengejutkan',
  'terbukti','bahaya','penting','terbaik','terburuk','kaget','serius','hebat',
  'hancur','menang','kalah','wow','insane','crazy','secret','shocking',
  'unbelievable','amazing','worst','best','danger','dangerous','mistake',
  'truth','finally','never','always','proof','fail','win','lost','surprise',
  'powerful'
]);

function tokenize(value: string): string[] {
  return (value.toLocaleLowerCase('id-ID').match(/[\p{L}\p{N}]{4,}/gu) || [])
    .filter(word => !STOP_WORDS.has(word));
}

/** Suggestions are visual metadata only; the source transcript is never edited. */
export function suggestCaptionHighlights(clips: ViralClip[], transcript: TranscriptLine[] = []): string[] {
  const scores = new Map<string, { display: string; score: number }>();
  const add = (word: string, weight: number) => {
    const key = word.toLocaleLowerCase('id-ID');
    if (key.length < 4 || STOP_WORDS.has(key)) return;
    const current = scores.get(key);
    if (current) current.score += weight;
    else scores.set(key, { display: word, score: weight });
  };
  for (const clip of clips) {
    for (const quote of clip.key_quotes || []) for (const word of tokenize(quote)) add(word, 4);
    for (const word of tokenize(clip.title || '')) add(word, 1);
    for (const word of tokenize(clip.title_suggestion || '')) add(word, 1);
  }
  for (const line of transcript) {
    for (const word of tokenize(line.text || '')) if (IMPACT_WORDS.has(word)) add(word, 3);
  }
  return [...scores.values()]
    .filter(item => item.score >= 3)
    .sort((a, b) => b.score - a.score || a.display.localeCompare(b.display))
    .slice(0, 12)
    .map(item => item.display);
}

export function getCaptionHighlightTerms(
  clips: ViralClip[],
  transcript: TranscriptLine[],
  autoHighlight: boolean,
  manualTerms: string[]
): string[] {
  const automatic = autoHighlight ? suggestCaptionHighlights(clips, transcript) : [];
  const combined = [...automatic, ...manualTerms].map(term => term.trim()).filter(Boolean);
  return [...new Map(combined.map(term => [term.toLocaleLowerCase('id-ID'), term])).values()].slice(0, 40);
}
