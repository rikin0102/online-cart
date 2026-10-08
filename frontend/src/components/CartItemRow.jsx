import React from 'react';
import { formatPrice } from './ProductCard';
import { getProductImage } from '../utils/productImages';

const CartItemRow = ({
  item,
  onUpdateQuantity,
  onRemove,
  isOperating,
  isMobile = false,
}) => {
  const imageUrl = getProductImage(item);

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
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <img
              src={imageUrl}
              alt={item.name}
              className="cart-product-thumb"
              onError={(e) => {
                e.target.onerror = null;
                e.target.src = 'https://images.unsplash.com/photo-1526738549149-8e07eca6c147?auto=format&fit=crop&w=600&q=80';
              }}
            />
            <div>
              <div className="cart-product-name">{item.name}</div>
              <div style={{ fontSize: '13px', color: 'var(--text-muted)', marginTop: '2px' }}>
                Unit: {formatPrice(item.price)}
              </div>
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
          <img
            src={imageUrl}
            alt={item.name}
            className="cart-product-thumb"
            onError={(e) => {
              e.target.onerror = null;
              e.target.src = 'https://images.unsplash.com/photo-1526738549149-8e07eca6c147?auto=format&fit=crop&w=600&q=80';
            }}
          />
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
