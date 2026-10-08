import { getProductImage } from '../utils/productImages';

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

  const imageUrl = getProductImage(product);

  return (
    <div className="product-card" id={`product-card-${product.id}`}>
      <div className="product-visual">
        <img
          src={imageUrl}
          alt={product.name}
          className="product-image"
          loading="lazy"
          onError={(e) => {
            e.target.onerror = null;
            e.target.src = 'https://images.unsplash.com/photo-1526738549149-8e07eca6c147?auto=format&fit=crop&w=600&q=80';
          }}
        />
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
