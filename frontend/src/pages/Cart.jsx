import React, { useState, useEffect, useCallback } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  fetchCart as apiFetchCart,
  updateItemQuantity as apiUpdateItemQuantity,
  removeItemFromCart as apiRemoveItemFromCart,
  submitOrder as apiSubmitOrder,
  extractErrorMessage,
} from '../api';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../components/Toast';
import CartItemRow from '../components/CartItemRow';
import { formatPrice } from '../components/ProductCard';
import '../styles/cart.css';

const CACHE_CART_KEY = 'online_cart_cached_data';

const Cart = () => {
  // 1. Instant hydration from cache for 0ms initial render
  const [cart, setCart] = useState(() => {
    try {
      const cached = typeof window !== 'undefined' ? localStorage.getItem(CACHE_CART_KEY) : null;
      return cached ? JSON.parse(cached) : { items: [], grand_total: 0, item_count: 0 };
    } catch {
      return { items: [], grand_total: 0, item_count: 0 };
    }
  });

  const [loading, setLoading] = useState(() => {
    try {
      const cached = typeof window !== 'undefined' ? localStorage.getItem(CACHE_CART_KEY) : null;
      return !cached;
    } catch {
      return true;
    }
  });

  const [isRefreshing, setIsRefreshing] = useState(false);
  const [loadError, setLoadError] = useState(null);
  const [operatingProductId, setOperatingProductId] = useState(null);
  const [isSubmittingOrder, setIsSubmittingOrder] = useState(false);

  const { setCartCount } = useAuth();
  const { toastSuccess, toastError, toastWarning } = useToast();
  const navigate = useNavigate();

  const loadCart = useCallback(async (isManualRetry = false) => {
    if (cart.items?.length > 0 && !isManualRetry) {
      setIsRefreshing(true);
    } else {
      setLoading(true);
    }
    setLoadError(null);

    try {
      const data = await apiFetchCart();
      setCart(data);
      setCartCount(data.item_count || 0);
      try {
        localStorage.setItem(CACHE_CART_KEY, JSON.stringify(data));
      } catch (e) {
        console.warn('Failed to cache cart:', e);
      }
    } catch (err) {
      console.error('Failed to load cart:', err);
      const errMsg = extractErrorMessage(err, 'Could not retrieve your cart. The server may be waking up.');
      setLoadError(errMsg);
      if (!cart.items || cart.items.length === 0) {
        toastError(errMsg);
      }
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  }, [cart.items, setCartCount, toastError]);

  useEffect(() => {
    loadCart();
  }, [loadCart]);

  const handleUpdateQuantity = async (productId, newQuantity) => {
    setOperatingProductId(productId);
    try {
      const data = await apiUpdateItemQuantity(productId, newQuantity);
      setCart(data);
      setCartCount(data.item_count || 0);
      toastSuccess('Cart updated.');
    } catch (err) {
      const message = extractErrorMessage(err, 'Failed to update quantity.');
      toastError(message);
    } finally {
      setOperatingProductId(null);
    }
  };

  const handleRemoveItem = async (productId) => {
    setOperatingProductId(productId);
    try {
      const data = await apiRemoveItemFromCart(productId);
      setCart(data);
      setCartCount(data.item_count || 0);
      toastSuccess('Item removed from cart.');
    } catch (err) {
      const message = extractErrorMessage(err, 'Failed to remove item.');
      toastError(message);
    } finally {
      setOperatingProductId(null);
    }
  };

  const handlePlaceOrder = async () => {
    if (!cart.items || cart.items.length === 0) {
      toastError('Your cart is empty.');
      return;
    }

    setIsSubmittingOrder(true);
    try {
      const orderData = await apiSubmitOrder();

      setCartCount(0);

      if (orderData.email_status === 'sent') {
        toastSuccess('Order placed successfully! Summary sent to your email.');
      } else {
        toastWarning('Order placed successfully. Email delivery could not be completed.');
      }

      navigate('/order-success', { state: { order: orderData } });
    } catch (err) {
      const message = extractErrorMessage(err, 'Failed to submit order. Please try again.');
      toastError(message);
    } finally {
      setIsSubmittingOrder(false);
    }
  };

  if (loading) {
    return (
      <div className="container">
        <div className="loading-center">
          <div className="spinner"></div>
          <p>Loading your shopping cart...</p>
        </div>
      </div>
    );
  }

  const isEmpty = !cart.items || cart.items.length === 0;

  if (isEmpty) {
    if (loadError) {
      return (
        <div className="container">
          <div className="error-fallback-card">
            <svg className="error-fallback-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75">
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="8" x2="12" y2="12" />
              <line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
            <h2>Unable to Retrieve Cart</h2>
            <p>{loadError}</p>
            <button className="btn-primary" onClick={() => loadCart(true)}>
              Retry Loading Cart
            </button>
          </div>
        </div>
      );
    }

    return (
      <div className="container">
        <div className="empty-state">
          <svg
            className="empty-state-icon"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
          >
            <path d="M7 18c-1.1 0-1.99.9-1.99 2S5.9 22 7 22s2-.9 2-2-.9-2-2-2zM1 2v2h2l3.6 7.59-1.35 2.45c-.16.28-.25.61-.25.96 0 1.1.9 2 2 2h12v-2H7.42c-.14 0-.25-.11-.25-.25l.03-.12.9-1.63h7.45c.75 0 1.41-.41 1.75-1.03l3.58-6.49A1.003 1.003 0 0 0 20 4H5.21l-.94-2H1zm16 16c-1.1 0-1.99.9-1.99 2s.89 2 1.99 2 2-.9 2-2-.9-2-2-2z" />
          </svg>
          <h2 className="empty-state-title">Your cart is empty</h2>
          <p className="empty-state-desc">Looks like you haven't added any items to your shopping cart yet.</p>
          <Link to="/dashboard" className="btn-primary" style={{ display: 'inline-block' }}>
            Continue shopping
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <div className="page-header">
        <h1 className="page-title">Shopping Cart</h1>
        <p className="page-subtitle">Review items in your cart before placing your order</p>
      </div>

      <div className="cart-layout">
        <div className="cart-items-container">
          {/* Desktop Table */}
          <table className="cart-table">
            <thead>
              <tr>
                <th>Product</th>
                <th>Price</th>
                <th>Quantity</th>
                <th>Line Total</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {cart.items.map((item) => (
                <CartItemRow
                  key={item.product_id}
                  item={item}
                  onUpdateQuantity={handleUpdateQuantity}
                  onRemove={handleRemoveItem}
                  isOperating={operatingProductId === item.product_id || isSubmittingOrder}
                  isMobile={false}
                />
              ))}
            </tbody>
          </table>

          {/* Mobile Stacked List */}
          <div className="cart-mobile-list">
            {cart.items.map((item) => (
              <CartItemRow
                key={item.product_id}
                item={item}
                onUpdateQuantity={handleUpdateQuantity}
                onRemove={handleRemoveItem}
                isOperating={operatingProductId === item.product_id || isSubmittingOrder}
                isMobile={true}
              />
            ))}
          </div>
        </div>

        {/* Order Summary Sidebar */}
        <div className="order-summary-card">
          <h2 className="summary-title">Order Summary</h2>

          <div className="summary-row">
            <span>Total Items</span>
            <span>{cart.item_count}</span>
          </div>

          <div className="summary-row">
            <span>Subtotal</span>
            <span>{formatPrice(cart.grand_total)}</span>
          </div>

          <div className="summary-row">
            <span>Standard Shipping</span>
            <span style={{ color: 'var(--success)' }}>Free</span>
          </div>

          <div className="summary-row total">
            <span>Grand Total</span>
            <span style={{ color: 'var(--primary)' }}>{formatPrice(cart.grand_total)}</span>
          </div>

          <button
            className="btn-primary btn-block"
            onClick={handlePlaceOrder}
            disabled={isSubmittingOrder || isEmpty}
            style={{ padding: '12px 16px', fontSize: '15px' }}
          >
            {isSubmittingOrder ? 'Placing order...' : 'Place order'}
          </button>

          <div style={{ marginTop: '16px', textAlign: 'center' }}>
            <Link to="/dashboard" style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
              &larr; Continue shopping
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Cart;
