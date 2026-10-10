import React, { useState, useEffect } from 'react';
import { subscribeServerWarming } from '../api';

const ServerWakeupNotice = () => {
  const [isWarming, setIsWarming] = useState(false);

  useEffect(() => {
    const unsubscribe = subscribeServerWarming((warming) => {
      setIsWarming(warming);
    });
    return unsubscribe;
  }, []);

  if (!isWarming) return null;

  return (
    <div className="server-wakeup-banner" role="status" aria-live="polite">
      <div className="server-wakeup-content">
        <span className="server-wakeup-icon">⚡</span>
        <div className="server-wakeup-text">
          <strong>Waking up cloud server...</strong> Render free tier enters sleep after inactivity.
          Your request is in progress and will complete automatically.
        </div>
      </div>
      <div className="server-wakeup-bar">
        <div className="server-wakeup-progress"></div>
      </div>
    </div>
  );
};

export default ServerWakeupNotice;
