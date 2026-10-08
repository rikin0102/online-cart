import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../components/Toast';
import { extractErrorMessage } from '../api/errorHandler';
import '../styles/auth.css';

const Register = () => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errorMsg, setErrorMsg] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { register, login, user } = useAuth();
  const { toastSuccess, toastError, toastInfo } = useToast();
  const navigate = useNavigate();

  // Redirect if already logged in
  useEffect(() => {
    if (user) {
      navigate('/dashboard', { replace: true });
    }
  }, [user, navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMsg('');

    const trimmedName = name.trim();
    const normalizedEmail = email.trim().toLowerCase();

    if (!trimmedName) {
      setErrorMsg('Please enter your full name.');
      return;
    }

    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    if (!normalizedEmail || !emailRegex.test(normalizedEmail)) {
      setErrorMsg('Please enter a valid email address (e.g. yourname@gmail.com).');
      return;
    }

    // Common typo warnings
    const domain = normalizedEmail.split('@')[1] || '';
    const typoMap = {
      'gmaill.com': 'gmail.com',
      'gamil.com': 'gmail.com',
      'gmal.com': 'gmail.com',
      'gmai.com': 'gmail.com',
      'gmaildotcom': 'gmail.com',
      'yaho.com': 'yahoo.com',
      'yahooo.com': 'yahoo.com',
      'hotmial.com': 'hotmail.com',
      'hotmai.com': 'hotmail.com',
      'outlok.com': 'outlook.com',
    };
    if (typoMap[domain]) {
      setErrorMsg(`Invalid email domain. Did you mean @${typoMap[domain]}? Please check your email.`);
      return;
    }

    const blockedDomains = [
      'fake.com', 'test.com', 'example.com', 'sample.com', 'tempmail.com',
      'mailinator.com', '10minutemail.com', 'guerrillamail.com', 'trashmail.com'
    ];
    if (blockedDomains.includes(domain)) {
      setErrorMsg('Temporary or disposable email addresses are not permitted. Please use a valid email.');
      return;
    }

    if (password.length < 8) {
      setErrorMsg('Password must be at least 8 characters long.');
      return;
    }

    setIsSubmitting(true);
    let registrationSucceeded = false;
    try {
      await register(trimmedName, normalizedEmail, password);
      registrationSucceeded = true;
      toastSuccess('Account created successfully!');
    } catch (err) {
      const message = extractErrorMessage(err, 'Failed to create account. Please try again.');
      setErrorMsg(message);
      toastError(message);
      setIsSubmitting(false);
      return;
    }

    // Auto-login after successful account creation
    try {
      await login(normalizedEmail, password);
      navigate('/dashboard', { replace: true });
    } catch (loginErr) {
      toastInfo('Account created! Please log in with your credentials.');
      navigate('/login', { replace: true });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="auth-wrapper">
      <div className="auth-card">
        <div className="auth-header">
          <h1 className="auth-title">Create an Account</h1>
          <p className="auth-subtitle">Join Online Cart to start shopping today</p>
        </div>

        {errorMsg && (
          <div className="auth-alert-error" role="alert" style={{ marginBottom: '16px' }}>
            {errorMsg}
          </div>
        )}

        <form onSubmit={handleSubmit} className="auth-form" noValidate>
          <div className="form-group">
            <label className="form-label" htmlFor="name-input">
              Full Name
            </label>
            <input
              id="name-input"
              type="text"
              className="form-input"
              placeholder="e.g. Rikin Patel"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              autoComplete="name"
              disabled={isSubmitting}
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="email-input">
              Email Address
            </label>
            <input
              id="email-input"
              type="email"
              className="form-input"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoComplete="email"
              disabled={isSubmitting}
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="password-input">
              Password
            </label>
            <input
              id="password-input"
              type="password"
              className="form-input"
              placeholder="Minimum 8 characters"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={8}
              autoComplete="new-password"
              disabled={isSubmitting}
            />
            <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
              Must be at least 8 characters.
            </span>
          </div>

          <button
            type="submit"
            className="btn-primary btn-block"
            style={{ marginTop: '8px' }}
            disabled={isSubmitting}
          >
            {isSubmitting ? 'Creating account...' : 'Register'}
          </button>
        </form>

        <div className="auth-footer">
          Already have an account? <Link to="/login">Log in</Link>
        </div>
      </div>
    </div>
  );
};

export default Register;
