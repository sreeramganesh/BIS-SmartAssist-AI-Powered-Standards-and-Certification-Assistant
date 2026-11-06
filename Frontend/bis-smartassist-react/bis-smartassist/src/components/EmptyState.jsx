import React from 'react';
import { BIS_LOGO_BASE64 } from '../utils/logo';

const TOPICS = [
  'What documents does CRS registration need?',
  'How long does registration take?',
  'Difference between ISI mark and CRS'
];

export default function EmptyState({ onPickTopic }) {
  return (
    <div className="empty-state">
      <div className="empty-icon">
        <img src={BIS_LOGO_BASE64} alt="BIS" />
      </div>
      <h2 className="empty-title">BIS SmartAssist Guidance</h2>
      <p className="empty-desc">
        Describe your manufactured product, import items, or ask any Indian Standard (IS),
        Compulsory Registration Scheme (CRS), or testing compliance question.
      </p>
      <div className="quick-topics" style={{ padding: 0 }}>
        {TOPICS.map(t => (
          <button key={t} onClick={() => onPickTopic(t)}>{t}</button>
        ))}
      </div>
    </div>
  );
}
