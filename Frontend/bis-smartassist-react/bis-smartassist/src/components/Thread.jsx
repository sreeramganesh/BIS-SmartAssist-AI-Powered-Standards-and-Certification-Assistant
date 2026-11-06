import React, { useEffect, useRef } from 'react';
import { BIS_LOGO_BASE64 } from '../utils/logo';

export default function Thread({ messages, isTyping }) {
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  return (
    <div className="thread-container">
      <div className="thread-watermark">
        <img src={BIS_LOGO_BASE64} alt="Watermark" />
      </div>
      <div className="thread">
        {messages.map(msg => (
          <div key={msg.id} className={`msg ${msg.role}`}>
            <div className="msg-inner">
              {msg.role === 'assistant' ? (
                <div className="avatar-mark">
                  <img src={BIS_LOGO_BASE64} alt="" />
                </div>
              ) : (
                <div className="avatar-mark user">You</div>
              )}

              <div className="msg-body">
                <div className="avatar-name">
                  {msg.role === 'assistant' ? 'BIS SmartAssist' : 'You'}
                  {msg.timestamp && <span className="msg-time">{msg.timestamp}</span>}
                </div>

                <div className="bubble">
                  {/* User-attached thumbnails / chips */}
                  {msg.attachments && msg.attachments.length > 0 && (
                    <div className="msg-attachments">
                      {msg.attachments.map((att, idx) => (
                        att.type === 'photo' ? (
                          <img key={idx} src={att.url} alt={att.name} className="msg-attachment-img" />
                        ) : (
                          <div key={idx} className="msg-attachment-doc">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                              <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" />
                              <polyline points="14 2 14 8 20 8" />
                            </svg>
                            <span>{att.name}</span>
                            {att.size && <span className="doc-size">({att.size})</span>}
                          </div>
                        )
                      ))}
                    </div>
                  )}

                  {/* Backend Uploaded Files Analysis Summary */}
                  {msg.uploaded_files && msg.uploaded_files.length > 0 && (
                    <div className="uploaded-files-status">
                      <div className="uf-header">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <polyline points="20 6 9 17 4 12" />
                        </svg>
                        <span>Document Intelligence Status ({msg.uploaded_files.length})</span>
                      </div>
                      <div className="uf-list">
                        {msg.uploaded_files.map((uf, uidx) => (
                          <span key={uidx} className={`uf-pill ${uf.status}`}>
                            {uf.filename} {uf.pages ? `(${uf.pages} pg)` : ''}
                            {uf.error ? ` — ${uf.error}` : ''}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {msg.paragraphs && msg.paragraphs.map((p, i) => <p key={i}>{p}</p>)}

                  {msg.citation && (
                    <div className="citation">
                      <span className="std">{msg.citation.std}</span>
                      {msg.citation.text}
                    </div>
                  )}

                  {(msg.confidence || msg.risk) && (
                    <div className="confidence-row">
                      {msg.confidence && <span className="tag confidence">{msg.confidence}</span>}
                      {msg.risk && <span className="tag risk">{msg.risk}</span>}
                    </div>
                  )}

                  {msg.steps && (
                    <div className="next-steps">
                      <p>Next steps &amp; specifications</p>
                      <div className="step-list">
                        {msg.steps.map((st, idx) => (
                          <div key={idx} className="step">
                            <span className="num">{idx + 1}</span>
                            <span>{st}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Multimodal & BIS Sources Block */}
                  {msg.sources && msg.sources.length > 0 && (
                    <div className="sources-block">
                      <div className="sources-header">
                        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                          <polyline points="14 2 14 8 20 8" />
                          <line x1="16" y1="13" x2="8" y2="13" />
                          <line x1="16" y1="17" x2="8" y2="17" />
                        </svg>
                        <span>Verified References ({msg.sources.length})</span>
                      </div>
                      <div className="sources-chips">
                        {msg.sources.map((s, idx) => (
                          <div
                            key={idx}
                            className={`source-chip ${s.type === 'uploaded_document' ? 'user-doc' : 'bis-doc'}`}
                            title={`${s.source} (Page ${s.page || 'N/A'}) - ${s.type === 'uploaded_document' ? 'User Attached Document' : 'Official BIS Knowledge Base'}`}
                          >
                            <span className={`source-std ${s.type === 'uploaded_document' ? 'user-doc-badge' : ''}`}>
                              {s.type === 'uploaded_document' ? 'User Doc' : (s.standard || 'BIS Standard')}
                            </span>
                            <span className="source-name">{s.source}</span>
                            {s.page && <span className="source-page">p. {s.page}</span>}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {msg.offlineNotice && (
                    <div className="offline-notice">
                      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <circle cx="12" cy="12" r="10" />
                        <line x1="12" y1="8" x2="12" y2="12" />
                        <line x1="12" y1="16" x2="12.01" y2="16" />
                      </svg>
                      <span>{msg.offlineNotice}</span>
                    </div>
                  )}

                  {msg.text && !msg.paragraphs && <p>{msg.text}</p>}
                </div>
              </div>
            </div>
          </div>
        ))}

        {isTyping && (
          <div className="msg assistant">
            <div className="msg-inner">
              <div className="avatar-mark">
                <img src={BIS_LOGO_BASE64} alt="" />
              </div>
              <div className="msg-body">
                <div className="avatar-name">BIS SmartAssist</div>
                <div className="bubble">
                  <div className="typing">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
}
