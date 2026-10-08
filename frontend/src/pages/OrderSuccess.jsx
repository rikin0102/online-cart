import React from 'react';
import { useLocation, Link, Navigate } from 'react-router-dom';
import { formatPrice } from '../components/ProductCard';
import '../styles/cart.css';

const OrderSuccess = () => {
  const location = useLocation();
  const order = location.state?.order;

  if (!order) {
    return <Navigate to="/dashboard" replace />;
  }

  const isEmailSent = order.email_status === 'sent';

  return (
    <div className="container">
      <div className="success-card">
        <div className="success-header">
          <div className="success-icon-badge">
            <svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" strokeWidth="2.5">
              <polyline points="20 6 9 17 4 12" />
            </svg>
          </div>
          <h1 className="success-title">Order Placed Successfully!</h1>
          <p className="success-order-id">Order Reference: #{order.id}</p>
        </div>

        {/* Email Status Alert */}
        <div className={`email-status-banner ${isEmailSent ? 'sent' : 'failed'}`}>
          <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2">
            {isEmailSent ? (
              <>
                <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" />
                <polyline points="22,6 12,13 2,6" />
              </>
            ) : (
              <>
                <circle cx="12" cy="12" r="10" />
                <line x1="12" y1="8" x2="12" y2="12" />
                <line x1="12" y1="16" x2="12.01" y2="16" />
              </>
            )}
          </svg>
          <div>
            {isEmailSent
              ? 'Order placed successfully. Your order summary has been sent to your email.'
              : 'Order placed, but we could not send the email.'}
          </div>
        </div>

        {/* Purchased Items List */}
        <div className="success-items-list">
          <h3 style={{ fontSize: '16px', fontWeight: 600, marginBottom: '12px', color: 'var(--text-main)' }}>
            Order Items
          </h3>
          {order.items &&
            order.items.map((item, idx) => (
              <div key={item.id || idx} className="success-item-row">
                <div>
                  <span style={{ fontWeight: 500, color: 'var(--text-main)' }}>{item.product_name}</span>
                  <span style={{ color: 'var(--text-muted)', fontSize: '13px', marginLeft: '8px' }}>
                    &times; {item.quantity} ({formatPrice(item.price)} each)
                  </span>
                </div>
                <div style={{ fontWeight: 600, color: 'var(--text-main)' }}>
                  {formatPrice(item.line_total)}
                </div>
              </div>
            ))}

          <div className="success-total-row">
            <span>Grand Total</span>
            <span style={{ color: 'var(--primary)' }}>{formatPrice(order.grand_total)}</span>
          </div>
        </div>

        <div style={{ textAlign: 'center', marginTop: '32px' }}>
          <Link to="/dashboard" className="btn-primary" style={{ display: 'inline-block', padding: '10px 24px' }}>
            Continue shopping
          </Link>
        </div>
      </div>
    </div>
  );
};

export default OrderSuccess;
