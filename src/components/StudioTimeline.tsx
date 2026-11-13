import React from 'react';
import type { TranscriptLine } from '../types';

interface StudioTimelineProps {
  start: number;
  end: number;
  currentTime: number;
  transcript: TranscriptLine[];
  onSeek: (time: number) => void;
}

function formatTime(seconds: number): string {
  const safe = Math.max(0, seconds);
  const minutes = Math.floor(safe / 60);
  const remainder = Math.floor(safe % 60);
  return `${minutes}:${String(remainder).padStart(2, '0')}`;
}

export const StudioTimeline: React.FC<StudioTimelineProps> = ({
  start,
  end,
  currentTime,
  transcript,
  onSeek,
}) => {
  const duration = Math.max(0.01, end - start);
  const playhead = Math.max(0, Math.min(100, ((currentTime - start) / duration) * 100));
  const visibleLines = transcript.filter((line) =>
    Number.isFinite(line.start) &&
    Number.isFinite(line.end) &&
    line.end > start &&
    line.start < end &&
    line.end > line.start
  );

  return (
    <section className="studio-timeline" aria-label="Timeline video dan subtitle">
      <div className="studio-timeline-heading">
        <span>TIMELINE</span>
        <span>{formatTime(currentTime)} / {formatTime(end - start)}</span>
      </div>

      <div className="studio-timeline-track-row">
        <span className="studio-timeline-track-label">VIDEO</span>
        <div className="studio-timeline-track studio-timeline-video-track">
          <div className="studio-timeline-video-segment" />
          <div className="studio-timeline-playhead" style={{ left: `${playhead}%` }} />
        </div>
      </div>

      <div className="studio-timeline-track-row">
        <span className="studio-timeline-track-label">CAPTION</span>
        <div className="studio-timeline-track studio-timeline-caption-track">
          {visibleLines.length > 0 ? visibleLines.map((line, index) => {
            const left = Math.max(0, ((line.start - start) / duration) * 100);
            const right = Math.min(100, ((line.end - start) / duration) * 100);
            const width = Math.max(0.8, right - left);
            return (
              <button
                key={`${line.start}-${line.end}-${index}`}
                type="button"
                className="studio-timeline-caption-block"
                style={{ left: `${left}%`, width: `${width}%` }}
                onClick={() => onSeek(Math.max(start, Math.min(end, line.start)))}
                title={line.text}
                aria-label={`Seek to caption: ${line.text}`}
              />
            );
          }) : (
            <span className="studio-timeline-empty">Transkrip belum tersedia</span>
          )}
          <div className="studio-timeline-playhead" style={{ left: `${playhead}%` }} />
        </div>
      </div>

      <div className="studio-timeline-scale">
        <span>{formatTime(start)}</span>
        <span>{formatTime(start + duration / 2)}</span>
        <span>{formatTime(end)}</span>
      </div>
    </section>
  );
};
