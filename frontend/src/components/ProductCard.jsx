import React from 'react';

// Minimal inline SVG category icons (no external images)
const getCategoryIcon = (category, name) => {
  const n = name.toLowerCase();
  const c = category.toLowerCase();

  if (n.includes('mouse pad')) {
    return (
      <svg className="product-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <rect x="2" y="5" width="20" height="14" rx="2" />
        <line x1="2" y1="10" x2="22" y2="10" />
      </svg>
    );
  }
  if (n.includes('mouse')) {
    return (
      <svg className="product-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <rect x="6" y="3" width="12" height="18" rx="6" />
        <line x1="12" y1="7" x2="12" y2="11" />
      </svg>
    );
  }
  if (n.includes('keyboard')) {
    return (
      <svg className="product-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <rect x="2" y="4" width="20" height="16" rx="2" />
        <line x1="6" y1="8" x2="6.01" y2="8" />
        <line x1="10" y1="8" x2="10.01" y2="8" />
        <line x1="14" y1="8" x2="14.01" y2="8" />
        <line x1="18" y1="8" x2="18.01" y2="8" />
        <line x1="7" y1="16" x2="17" y2="16" />
      </svg>
    );
  }
  if (n.includes('headphone') || c.includes('audio')) {
    return (
      <svg className="product-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M3 18v-6a9 9 0 0 1 18 0v6" />
        <path d="M21 19a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3zM3 19a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2v-3a2 2 0 0 0-2-2H3z" />
      </svg>
    );
  }
  if (n.includes('webcam') || c.includes('peripheral')) {
    return (
      <svg className="product-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <circle cx="12" cy="10" r="7" />
        <circle cx="12" cy="10" r="3" />
        <line x1="12" y1="17" x2="12" y2="21" />
        <line x1="8" y1="21" x2="16" y2="21" />
      </svg>
    );
  }
  if (n.includes('lamp') || c.includes('light')) {
    return (
      <svg className="product-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M9 18h6M10 22h4M6 10a6 6 0 1 1 12 0c0 2.5-1.5 4.5-3 5.5v.5H9v-.5C7.5 14.5 6 12.5 6 10z" />
      </svg>
    );
  }
  if (n.includes('stand')) {
    return (
      <svg className="product-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M4 19h16M7 19l4-14h2l4 14" />
      </svg>
    );
  }
  if (n.includes('cable')) {
    return (
      <svg className="product-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M4 12h8a4 4 0 0 1 4 4v4M20 20h-4M4 8h8a8 8 0 0 1 8 8" />
      </svg>
    );
  }
  if (n.includes('power') || c.includes('power')) {
    return (
      <svg className="product-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <rect x="5" y="2" width="14" height="20" rx="2" />
        <line x1="11" y1="12" x2="13" y2="12" />
        <line x1="12" y1="11" x2="12" y2="13" />
      </svg>
    );
  }

  // Default box icon
  return (
    <svg className="product-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" />
    </svg>
  );
};

export const formatPrice = (price) => {
  const num = Number(price);
  return `Rs. ${num.toLocaleString('en-IN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
};

const ProductCard = ({
  product,
  cartItem,
  onAddToCart,
  onUpdateQuantity,
  onRemoveFromCart,
  isOperating,
}) => {
  const inCart = !!cartItem;
  const quantity = cartItem?.quantity || 0;

  const handleIncrement = () => {
    if (quantity < 99) {
      onUpdateQuantity(product.id, quantity + 1);
    }
  };

  const handleDecrement = () => {
    if (quantity > 1) {
      onUpdateQuantity(product.id, quantity - 1);
    } else {
      onRemoveFromCart(product.id);
    }
  };

  return (
    <div className="product-card" id={`product-card-${product.id}`}>
      <div className="product-visual">
        {getCategoryIcon(product.category, product.name)}
        <span className="product-category">{product.category}</span>
      </div>

      <h3 className="product-name">{product.name}</h3>
      <p className="product-description">{product.description}</p>

      <div className="product-card-footer">
        <span className="product-price">{formatPrice(product.price)}</span>

        {inCart ? (
          <div className="quantity-stepper" aria-label={`Quantity for ${product.name}`}>
            <button
              className="stepper-btn"
              onClick={handleDecrement}
              disabled={isOperating}
              aria-label="Decrease quantity"
              title="Decrease quantity"
            >
              &minus;
            </button>
            <span className="stepper-value" aria-live="polite">
              {quantity}
            </span>
            <button
              className="stepper-btn"
              onClick={handleIncrement}
              disabled={isOperating || quantity >= 99}
              aria-label="Increase quantity"
              title="Increase quantity"
            >
              +
            </button>
          </div>
        ) : (
          <button
            className="btn-primary"
            onClick={() => onAddToCart(product.id)}
            disabled={isOperating}
          >
            {isOperating ? 'Adding...' : 'Add to cart'}
          </button>
        )}
      </div>
    </div>
  );
};

export default ProductCard;
