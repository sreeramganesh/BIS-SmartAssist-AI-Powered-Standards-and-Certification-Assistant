import React from 'react';
import BrandLogo from './BrandLogo';

export default function Sidebar({
  currentUser,
  onNewChat,
  conversations,
  activeConvId,
  onSelectConv,
  onTogglePin,
  onDeleteConv,
  onLogout
}) {
  const pinnedConvs = conversations.filter(c => c.pinned);
  const recentConvs = conversations.filter(c => !c.pinned);

  return (
    <aside className="sidebar">
      <div className="brand">
        <BrandLogo size={30} imgSize={24} />
        <div className="brand-text">
          <h1>BIS <span className="accent">SmartAssist</span></h1>
        </div>
      </div>

      {currentUser && (
        <div className="user-profile-card">
          <div className="user-info">
            <div className="user-avatar">
              {currentUser.name && currentUser.name.trim() ? currentUser.name.trim().charAt(0).toUpperCase() : 'U'}
            </div>
            <div className="user-details">
              <div className="user-name">{currentUser.name || 'User'}</div>
              <div className="user-email">{currentUser.email}</div>
            </div>
          </div>
          <button className="logout-btn" onClick={onLogout} title="Log Out">Log out</button>
        </div>
      )}

      <button className="new-chat" onClick={onNewChat}>
        <span>+</span> New enquiry
      </button>

      {pinnedConvs.length > 0 && (
        <div className="nav-group">
          <h2>
            <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
              <path d="M16 12V4h1V2H7v2h1v8l-2 2v2h5v6l1 1 1-1v-6h5v-2l-2-2z" />
            </svg>
            {' Pinned Enquiries'}
          </h2>
          <div className="history-list">
            {pinnedConvs.map(c => (
              <div
                key={c.id}
                className={`history-item ${activeConvId === c.id ? 'active' : ''}`}
                onClick={() => onSelectConv(c.id)}
              >
                <div className="history-content">
                  <div className="history-title">{c.title}</div>
                  <div className="history-time">{c.formattedTime}</div>
                </div>
                <div className="history-actions">
                  <button
                    className="action-btn pinned"
                    title="Unpin conversation"
                    onClick={(e) => { e.stopPropagation(); onTogglePin(c.id); }}
                  >
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M16 12V4h1V2H7v2h1v8l-2 2v2h5v6l1 1 1-1v-6h5v-2l-2-2z" />
                    </svg>
                  </button>
                  <button
                    className="action-btn"
                    title="Delete conversation"
                    onClick={(e) => { e.stopPropagation(); onDeleteConv(c.id); }}
                  >
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2" />
                    </svg>
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {recentConvs.length > 0 && (
        <div className="nav-group">
          <h2>Recent Enquiries</h2>
          <div className="history-list">
            {recentConvs.map(c => (
              <div
                key={c.id}
                className={`history-item ${activeConvId === c.id ? 'active' : ''}`}
                onClick={() => onSelectConv(c.id)}
              >
                <div className="history-content">
                  <div className="history-title">{c.title}</div>
                  <div className="history-time">{c.formattedTime}</div>
                </div>
                <div className="history-actions">
                  <button
                    className="action-btn"
                    title="Pin conversation"
                    onClick={(e) => { e.stopPropagation(); onTogglePin(c.id); }}
                  >
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M16 12V4h1V2H7v2h1v8l-2 2v2h5v6l1 1 1-1v-6h5v-2l-2-2z" />
                    </svg>
                  </button>
                  <button
                    className="action-btn"
                    title="Delete conversation"
                    onClick={(e) => { e.stopPropagation(); onDeleteConv(c.id); }}
                  >
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2" />
                    </svg>
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="sidebar-foot">
        Answers are grounded in official BIS publications. Verified guidance does not replace certification by a licensed body.
      </div>
    </aside>
  );
}
