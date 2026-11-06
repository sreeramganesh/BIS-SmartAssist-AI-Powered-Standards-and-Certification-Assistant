import React from 'react';

export default function Topbar({ title, activeConv, onTogglePin }) {
  return (
    <div className="topbar">
      <h2>
        {title || 'BIS SmartAssist'}
        {activeConv && (
          <button
            className={`action-btn ${activeConv.pinned ? 'pinned' : ''}`}
            style={{ marginLeft: '8px' }}
            title={activeConv.pinned ? 'Unpin enquiry' : 'Pin enquiry'}
            onClick={() => onTogglePin(activeConv.id)}
          >
            <svg width="15" height="15" viewBox="0 0 24 24" fill={activeConv.pinned ? 'currentColor' : 'none'} stroke="currentColor" strokeWidth="2">
              <path d="M16 12V4h1V2H7v2h1v8l-2 2v2h5v6l1 1 1-1v-6h5v-2l-2-2z" />
            </svg>
          </button>
        )}
      </h2>
      <div className="status">
        <span className="pulse" />
        Sources: bis.gov.in
      </div>
    </div>
  );
}
