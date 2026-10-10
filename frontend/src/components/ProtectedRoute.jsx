import React, { useState, useEffect } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();
  const location = useLocation();
  const [showWarmingHint, setShowWarmingHint] = useState(false);

  useEffect(() => {
    let timer;
    if (loading) {
      timer = setTimeout(() => {
        setShowWarmingHint(true);
      }, 2500);
    } else {
      setShowWarmingHint(false);
    }
    return () => clearTimeout(timer);
  }, [loading]);

  if (loading) {
    return (
      <div className="loading-center" style={{ minHeight: '80vh' }}>
        <div className="spinner"></div>
        <p style={{ fontWeight: 500 }}>Connecting to your account...</p>
        {showWarmingHint && (
          <p style={{ fontSize: '12px', color: 'var(--text-muted)', maxWidth: '320px', textAlign: 'center' }}>
            Cloud server is waking up from idle state. Thank you for your patience...
          </p>
        )}
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return children;
};

export default ProtectedRoute;
