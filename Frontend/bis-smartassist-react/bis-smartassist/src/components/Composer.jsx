import React, { useRef, useEffect } from 'react';

export default function Composer({
  value,
  onChange,
  onSend,
  stagedAttachments,
  onRemoveStaged,
  onAddPhotos,
  onAddDocs,
  validationError
}) {
  const textareaRef = useRef(null);
  const photoInputRef = useRef(null);
  const docInputRef = useRef(null);

  useEffect(() => {
    if (textareaRef.current) {
      if (!value) {
        textareaRef.current.style.height = 'auto';
      } else {
        textareaRef.current.style.height = 'auto';
        textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 120) + 'px';
      }
    }
  }, [value]);

  const handleTextChange = (e) => {
    onChange(e.target.value);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      onSend();
    }
  };

  return (
    <div className="composer">
      <div className="composer-inner">
        {validationError && (
          <div className="upload-error-banner" role="alert">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="8" x2="12" y2="12" />
              <line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
            <span>{validationError}</span>
          </div>
        )}

        <div className="composer-box">
          {stagedAttachments.length > 0 && (
            <div className="composer-staged">
              {stagedAttachments.map((file) => (
                <div key={file.id} className="staged-chip" title={`${file.name} (${file.size || 'Attachment'})`}>
                  {file.type === 'photo' ? (
                    <img src={file.url} alt="upload preview" />
                  ) : (
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" />
                      <polyline points="14 2 14 8 20 8" />
                    </svg>
                  )}
                  <span className="staged-name">{file.name}</span>
                  {file.size && <span className="staged-size">({file.size})</span>}
                  <button className="remove-btn" title="Remove attachment" onClick={() => onRemoveStaged(file.id)}>×</button>
                </div>
              ))}
            </div>
          )}

          <div className="composer-row">
            <textarea
              ref={textareaRef}
              rows={1}
              placeholder="Describe your product, ask a question, or analyze attached documents…"
              value={value}
              onChange={handleTextChange}
              onKeyDown={handleKeyDown}
            />
            <div className="composer-actions">
              <input
                type="file"
                ref={photoInputRef}
                accept="image/png,image/jpeg,image/jpg"
                multiple
                style={{ display: 'none' }}
                onChange={onAddPhotos}
              />
              <input
                type="file"
                ref={docInputRef}
                accept=".pdf,.png,.jpg,.jpeg"
                multiple
                style={{ display: 'none' }}
                onChange={onAddDocs}
              />

              <button
                type="button"
                className="attach-btn"
                title="Attach Photo / Label (PNG, JPG)"
                onClick={() => photoInputRef.current && photoInputRef.current.click()}
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M23 19a2 2 0 01-2 2H3a2 2 0 01-2-2V8a2 2 0 012-2h4l2-3h6l2 3h4a2 2 0 012 2z" />
                  <circle cx="12" cy="13" r="4" />
                </svg>
              </button>

              <button
                type="button"
                className="attach-btn"
                title="Attach Document (PDF, Images)"
                onClick={() => docInputRef.current && docInputRef.current.click()}
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M21.44 11.05l-9.19 9.19a6 6 0 01-8.49-8.49l9.19-9.19a4 4 0 015.66 5.66l-9.2 9.19a2 2 0 01-2.83-2.83l8.49-8.48" />
                </svg>
              </button>

              <button
                className="send-btn"
                onClick={onSend}
                disabled={!value.trim() && stagedAttachments.length === 0}
                aria-label="Send"
              >
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                  <path d="M2 8H14M14 8L9 3M14 8L9 13" stroke="white" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </button>
            </div>
          </div>
        </div>
        <p className="composer-note">
          Responses cite official BIS sources. Final compliance determinations rest with BIS and licensed certification bodies.
        </p>
      </div>
    </div>
  );
}
