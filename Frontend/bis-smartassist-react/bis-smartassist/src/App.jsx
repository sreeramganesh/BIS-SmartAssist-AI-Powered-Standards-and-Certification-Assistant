import React, { useState, useEffect, useRef } from 'react';
import AuthScreen from './components/AuthScreen';
import Sidebar from './components/Sidebar';
import Topbar from './components/Topbar';
import EmptyState from './components/EmptyState';
import Thread from './components/Thread';
import Composer from './components/Composer';
import { formatDateTime } from './utils/bisAnswers';
import { sendChatToBIS, sendChatWithFilesToBIS } from './utils/bisApi';
import './index.css';

const MAX_FILES = 5;
const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10 MB

export default function App() {
  const [currentUser, setCurrentUser] = useState(() => {
    try {
      const session = localStorage.getItem('bis_session');
      return session ? JSON.parse(session) : null;
    } catch (e) {
      return null;
    }
  });

  const currentUserRef = useRef(currentUser);
  useEffect(() => {
    currentUserRef.current = currentUser;
  }, [currentUser]);

  const [conversations, setConversations] = useState([]);
  const [activeConvId, setActiveConvId] = useState(null);
  const [composerText, setComposerText] = useState('');
  const [stagedAttachments, setStagedAttachments] = useState([]);
  const [validationError, setValidationError] = useState('');
  const [isTyping, setIsTyping] = useState(false);

  // Pre-seed default user if no users exist
  useEffect(() => {
    try {
      const existingUsers = localStorage.getItem('bis_users');
      if (!existingUsers) {
        const defaultUsers = [{ name: 'Rahul Sharma', email: 'rahul@example.com', password: 'password123' }];
        localStorage.setItem('bis_users', JSON.stringify(defaultUsers));
      }
    } catch (e) {
      // Ignore storage errors
    }
  }, []);

  // Load user conversations from localStorage
  useEffect(() => {
    if (currentUser) {
      const saved = localStorage.getItem(`bis_conversations_${currentUser.email}`);
      if (saved) {
        try {
          setConversations(JSON.parse(saved));
        } catch (e) {
          setConversations([]);
        }
      } else {
        setConversations([]);
      }
    }
  }, [currentUser]);

  const saveConversations = (updated) => {
    setConversations(updated);
    if (currentUser) {
      localStorage.setItem(`bis_conversations_${currentUser.email}`, JSON.stringify(updated));
    }
  };

  const handleLogin = (user) => {
    setCurrentUser(user);
    localStorage.setItem('bis_session', JSON.stringify(user));
    setActiveConvId(null);
  };

  const handleLogout = () => {
    setCurrentUser(null);
    localStorage.removeItem('bis_session');
    setActiveConvId(null);
  };

  const handleNewChat = () => {
    setActiveConvId(null);
    setComposerText('');
    setStagedAttachments([]);
    setValidationError('');
  };

  const handleSelectConv = (id) => {
    setActiveConvId(id);
    setComposerText('');
    setStagedAttachments([]);
    setValidationError('');
  };

  const handleTogglePin = (id) => {
    const updated = conversations.map(c => c.id === id ? { ...c, pinned: !c.pinned } : c);
    saveConversations(updated);
  };

  const handleDeleteConv = (id) => {
    const updated = conversations.filter(c => c.id !== id);
    saveConversations(updated);
    if (activeConvId === id) {
      setActiveConvId(null);
    }
  };

  const validateAndStageFile = (file, type, dataUrl = null) => {
    const ext = file.name.slice(file.name.lastIndexOf('.')).toLowerCase();
    const allowed = ['.pdf', '.png', '.jpg', '.jpeg'];

    if (!allowed.includes(ext)) {
      return `File '${file.name}' is not supported. Only PDF, PNG, JPG, and JPEG files are allowed.`;
    }

    if (file.size > MAX_FILE_SIZE) {
      return `File '${file.name}' exceeds the 10 MB maximum size limit.`;
    }

    if (file.size === 0) {
      return `File '${file.name}' is empty (0 bytes).`;
    }

    const sizeStr = file.size < 1024 * 1024
      ? Math.round(file.size / 1024) + ' KB'
      : (file.size / (1024 * 1024)).toFixed(1) + ' MB';

    const newAttachment = {
      id: 'att_' + Date.now() + Math.random().toString(36).substring(2, 7),
      name: file.name,
      type: type,
      url: dataUrl || '#',
      size: sizeStr,
      rawFile: file
    };

    setStagedAttachments(prev => {
      if (prev.length >= MAX_FILES) {
        return prev;
      }
      return [...prev, newAttachment];
    });

    return null;
  };

  const handleAddPhotos = (e) => {
    setValidationError('');
    const files = Array.from(e.target.files);

    if (stagedAttachments.length + files.length > MAX_FILES) {
      setValidationError(`You can attach a maximum of ${MAX_FILES} files per question.`);
      e.target.value = '';
      return;
    }

    files.forEach(file => {
      const reader = new FileReader();
      reader.onload = (event) => {
        const err = validateAndStageFile(file, 'photo', event.target.result);
        if (err) setValidationError(err);
      };
      reader.readAsDataURL(file);
    });

    e.target.value = '';
  };

  const handleAddDocs = (e) => {
    setValidationError('');
    const files = Array.from(e.target.files);

    if (stagedAttachments.length + files.length > MAX_FILES) {
      setValidationError(`You can attach a maximum of ${MAX_FILES} files per question.`);
      e.target.value = '';
      return;
    }

    files.forEach(file => {
      const isImg = /\.(png|jpe?g)$/i.test(file.name);
      if (isImg) {
        const reader = new FileReader();
        reader.onload = (event) => {
          const err = validateAndStageFile(file, 'photo', event.target.result);
          if (err) setValidationError(err);
        };
        reader.readAsDataURL(file);
      } else {
        const err = validateAndStageFile(file, 'document', '#');
        if (err) setValidationError(err);
      }
    });

    e.target.value = '';
  };

  const handleRemoveStaged = (id) => {
    setStagedAttachments(prev => prev.filter(a => a.id !== id));
    setValidationError('');
  };

  const handleSendMessage = async (textOverride) => {
    const text = (textOverride || composerText).trim();
    if (!text && stagedAttachments.length === 0) return;

    setValidationError('');
    const sendingUserEmail = currentUser?.email;
    const timeStr = formatDateTime();

    // Prepare serializable attachments for local conversation storage (omit DOM rawFile)
    const storedAttachments = stagedAttachments.map(a => ({
      id: a.id,
      name: a.name,
      type: a.type,
      url: a.url,
      size: a.size
    }));

    const userMsg = {
      id: 'msg_' + Date.now(),
      role: 'user',
      text: text,
      attachments: storedAttachments,
      timestamp: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
    };

    let targetConvId = activeConvId;
    let updatedConvs = [...conversations];

    if (!targetConvId) {
      const newConv = {
        id: 'conv_' + Date.now(),
        title: text ? (text.length > 32 ? text.substring(0, 32) + '…' : text) : (stagedAttachments[0]?.name || 'Document Enquiry'),
        pinned: false,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        formattedTime: timeStr,
        messages: [userMsg]
      };
      targetConvId = newConv.id;
      updatedConvs = [newConv, ...conversations];
      setActiveConvId(targetConvId);
    } else {
      updatedConvs = conversations.map(c => {
        if (c.id === targetConvId) {
          return {
            ...c,
            updatedAt: new Date().toISOString(),
            formattedTime: timeStr,
            messages: [...c.messages, userMsg]
          };
        }
        return c;
      });
    }

    saveConversations(updatedConvs);

    // Collect raw files to transmit to backend
    const filesToUpload = stagedAttachments.map(a => a.rawFile).filter(Boolean);

    setComposerText('');
    setStagedAttachments([]);
    setIsTyping(true);

    try {
      let answerData;

      if (filesToUpload.length > 0) {
        // MULTIMODAL ROUTE: Transmits actual file binaries via multipart/form-data
        answerData = await sendChatWithFilesToBIS(text, filesToUpload);
      } else {
        // TEXT-ONLY ROUTE: Preserves standard JSON chat
        answerData = await sendChatToBIS(text);
      }

      const activeUser = currentUserRef.current;
      if (!activeUser || activeUser.email !== sendingUserEmail) {
        setIsTyping(false);
        return;
      }

      const botMsg = {
        id: 'msg_bot_' + Date.now(),
        role: 'assistant',
        timestamp: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
        ...answerData
      };

      setConversations(prev => {
        const next = prev.map(c => {
          if (c.id === targetConvId) {
            return { ...c, messages: [...c.messages, botMsg] };
          }
          return c;
        });
        if (activeUser && activeUser.email) {
          localStorage.setItem(`bis_conversations_${activeUser.email}`, JSON.stringify(next));
        }
        return next;
      });
    } catch (err) {
      console.error('Error querying BIS SmartAssist API:', err);
    } finally {
      setIsTyping(false);
    }
  };

  if (!currentUser) {
    return <AuthScreen onLogin={handleLogin} />;
  }

  const activeConv = conversations.find(c => c.id === activeConvId);
  const activeMessages = activeConv ? activeConv.messages : [];

  return (
    <div className="app-shell">
      <Sidebar
        currentUser={currentUser}
        onNewChat={handleNewChat}
        conversations={conversations}
        activeConvId={activeConvId}
        onSelectConv={handleSelectConv}
        onTogglePin={handleTogglePin}
        onDeleteConv={handleDeleteConv}
        onLogout={handleLogout}
      />
      <main className="main">
        <Topbar
          title={activeConv ? activeConv.title : 'BIS SmartAssist'}
          activeConv={activeConv}
          onTogglePin={handleTogglePin}
        />

        {!activeConvId || activeMessages.length === 0 ? (
          <EmptyState onPickTopic={(topic) => handleSendMessage(topic)} />
        ) : (
          <Thread messages={activeMessages} isTyping={isTyping} />
        )}

        <Composer
          value={composerText}
          onChange={setComposerText}
          onSend={() => handleSendMessage()}
          stagedAttachments={stagedAttachments}
          onRemoveStaged={handleRemoveStaged}
          onAddPhotos={handleAddPhotos}
          onAddDocs={handleAddDocs}
          validationError={validationError}
        />
      </main>
    </div>
  );
}
