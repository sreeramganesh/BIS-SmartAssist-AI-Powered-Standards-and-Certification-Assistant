import React, { useState } from 'react';
import BrandLogo from './BrandLogo';

export default function AuthScreen({ onLogin }) {
  const [isSignUp, setIsSignUp] = useState(false);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');

    if (!email.trim() || !password.trim()) {
      setError('Please fill in all required fields.');
      return;
    }

    let storedUsers = [];
    try {
      storedUsers = JSON.parse(localStorage.getItem('bis_users') || '[]');
      if (!Array.isArray(storedUsers)) storedUsers = [];
    } catch (e) {
      storedUsers = [];
    }

    if (isSignUp) {
      if (!name.trim()) {
        setError('Please enter your full name.');
        return;
      }
      const existing = storedUsers.find(u => u && u.email && u.email.toLowerCase() === email.toLowerCase());
      if (existing) {
        setError('An account with this email already exists.');
        return;
      }
      const newUser = { name: name.trim(), email: email.trim(), password };
      storedUsers.push(newUser);
      localStorage.setItem('bis_users', JSON.stringify(storedUsers));
      onLogin({ name: newUser.name, email: newUser.email });
    } else {
      const user = storedUsers.find(u => u && u.email && u.email.toLowerCase() === email.toLowerCase() && u.password === password);
      if (!user) {
        setError('Invalid email address or password.');
        return;
      }
      onLogin({ name: user.name, email: user.email });
    }
  };

  return (
    <div className="auth-wrapper">
      <div className="auth-card">
        <div className="auth-brand">
          <BrandLogo size={56} imgSize={42} />
          <h1>BIS SmartAssist</h1>
          <p>Sign in to access official compliance &amp; standards guidance</p>
        </div>

        <div className="auth-tabs">
          <button
            className={`auth-tab ${!isSignUp ? 'active' : ''}`}
            onClick={() => { setIsSignUp(false); setError(''); }}
          >
            Sign In
          </button>
          <button
            className={`auth-tab ${isSignUp ? 'active' : ''}`}
            onClick={() => { setIsSignUp(true); setError(''); }}
          >
            Sign Up
          </button>
        </div>

        {error && <div className="auth-error">{error}</div>}

        <form className="auth-form" onSubmit={handleSubmit}>
          {isSignUp && (
            <div className="form-group">
              <label>Full Name</label>
              <input
                type="text"
                className="form-input"
                placeholder="Rahul Sharma"
                value={name}
                onChange={e => setName(e.target.value)}
              />
            </div>
          )}

          <div className="form-group">
            <label>Email Address</label>
            <input
              type="email"
              className="form-input"
              placeholder="name@company.com"
              value={email}
              onChange={e => setEmail(e.target.value)}
            />
          </div>

          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              className="form-input"
              placeholder="••••••••"
              value={password}
              onChange={e => setPassword(e.target.value)}
            />
          </div>

          <button type="submit" className="auth-btn">
            {isSignUp ? 'Create Account' : 'Sign In'}
          </button>
        </form>
      </div>
    </div>
  );
}
