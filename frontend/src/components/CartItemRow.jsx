import React from 'react';
import { formatPrice } from './ProductCard';

const CartItemRow = ({
  item,
  onUpdateQuantity,
  onRemove,
  isOperating,
  isMobile = false,
}) => {
  const handleDecrement = () => {
    if (item.quantity > 1) {
      onUpdateQuantity(item.product_id, item.quantity - 1);
    } else {
      onRemove(item.product_id);
    }
  };

  const handleIncrement = () => {
    if (item.quantity < 99) {
      onUpdateQuantity(item.product_id, item.quantity + 1);
    }
  };

  if (isMobile) {
    return (
      <div className="cart-mobile-row" id={`mobile-cart-item-${item.product_id}`}>
        <div className="cart-mobile-header">
          <div>
            <div className="cart-product-name">{item.name}</div>
            <div style={{ fontSize: '13px', color: 'var(--text-muted)', marginTop: '2px' }}>
              Unit: {formatPrice(item.price)}
            </div>
          </div>
          <button
            className="btn-danger"
            style={{ padding: '4px 8px', fontSize: '12px' }}
            onClick={() => onRemove(item.product_id)}
            disabled={isOperating}
            title="Remove item"
          >
            Remove
          </button>
        </div>

        <div className="cart-mobile-actions">
          <div className="quantity-stepper">
            <button
              className="stepper-btn"
              onClick={handleDecrement}
              disabled={isOperating}
              aria-label="Decrease quantity"
            >
              &minus;
            </button>
            <span className="stepper-value">{item.quantity}</span>
            <button
              className="stepper-btn"
              onClick={handleIncrement}
              disabled={isOperating || item.quantity >= 99}
              aria-label="Increase quantity"
            >
              +
            </button>
          </div>

          <div className="cart-mobile-totals">
            <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Total: </span>
            <strong style={{ fontSize: '15px', color: 'var(--text-main)' }}>
              {formatPrice(item.line_total)}
            </strong>
          </div>
        </div>
      </div>
    );
  }

  // Desktop Table Row
  return (
    <tr id={`cart-row-${item.product_id}`}>
      <td>
        <div className="cart-product-cell">
          <div className="cart-product-icon">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="2" y="3" width="20" height="14" rx="2" />
              <line x1="8" y1="21" x2="16" y2="21" />
              <line x1="12" y1="17" x2="12" y2="21" />
            </svg>
          </div>
          <span className="cart-product-name">{item.name}</span>
        </div>
      </td>
      <td>{formatPrice(item.price)}</td>
      <td>
        <div className="quantity-stepper">
          <button
            className="stepper-btn"
            onClick={handleDecrement}
            disabled={isOperating}
            aria-label="Decrease quantity"
          >
            &minus;
          </button>
          <span className="stepper-value">{item.quantity}</span>
          <button
            className="stepper-btn"
            onClick={handleIncrement}
            disabled={isOperating || item.quantity >= 99}
            aria-label="Increase quantity"
          >
            +
          </button>
        </div>
      </td>
      <td>
        <strong>{formatPrice(item.line_total)}</strong>
      </td>
      <td>
        <button
          className="btn-danger"
          style={{ padding: '6px 12px', fontSize: '13px' }}
          onClick={() => onRemove(item.product_id)}
          disabled={isOperating}
        >
          Remove
        </button>
      </td>
    </tr>
  );
};

export default CartItemRow;
