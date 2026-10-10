import React, { useState, useEffect, useCallback, useMemo } from 'react';
import {
  fetchProducts,
  fetchCart,
  addItemToCart,
  updateItemQuantity,
  removeItemFromCart,
  extractErrorMessage,
} from '../api';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../components/Toast';
import ProductCard from '../components/ProductCard';
import '../styles/dashboard.css';

const CACHE_PRODUCTS_KEY = 'online_cart_cached_products';

const Dashboard = () => {
  // 1. Instant hydration from cache for 0ms initial render
  const [products, setProducts] = useState(() => {
    try {
      const cached = typeof window !== 'undefined' ? localStorage.getItem(CACHE_PRODUCTS_KEY) : null;
      return cached ? JSON.parse(cached) : [];
    } catch {
      return [];
    }
  });

  const [cartItemsMap, setCartItemsMap] = useState({});
  const [selectedCategory, setSelectedCategory] = useState('All');
  
  // Only show full loading screen if we don't even have cached products
  const [loading, setLoading] = useState(() => {
    try {
      const cached = typeof window !== 'undefined' ? localStorage.getItem(CACHE_PRODUCTS_KEY) : null;
      return !cached || JSON.parse(cached).length === 0;
    } catch {
      return true;
    }
  });

  const [isRefreshing, setIsRefreshing] = useState(false);
  const [loadError, setLoadError] = useState(null);
  const [operatingProductId, setOperatingProductId] = useState(null);

  const { setCartCount } = useAuth();
  const { toastSuccess, toastError, toastInfo } = useToast();

  const loadData = useCallback(async (isManualRetry = false) => {
    // If we have products, refresh silently in the background
    if (products.length > 0 && !isManualRetry) {
      setIsRefreshing(true);
    } else {
      setLoading(true);
    }
    setLoadError(null);

    try {
      const [productsData, cartData] = await Promise.all([
        fetchProducts(),
        fetchCart(),
      ]);

      setProducts(productsData);
      try {
        localStorage.setItem(CACHE_PRODUCTS_KEY, JSON.stringify(productsData));
      } catch (e) {
        console.warn('Failed to cache products:', e);
      }

      const itemsMap = {};
      if (cartData && Array.isArray(cartData.items)) {
        cartData.items.forEach((item) => {
          itemsMap[item.product_id] = item;
        });
      }
      setCartItemsMap(itemsMap);
      setCartCount(cartData?.item_count || 0);

      if (isManualRetry) {
        toastSuccess('Connected! Catalog updated.');
      }
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
      const errMsg = extractErrorMessage(err, 'Could not reach server. The cloud backend might be waking up.');
      setLoadError(errMsg);
      
      // If we already have cached products, don't break the user experience
      if (products.length > 0) {
        toastInfo('Using cached catalog while server connects.');
      } else {
        toastError(errMsg);
      }
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  }, [products.length, setCartCount, toastError, toastInfo, toastSuccess]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // Categories list
  const categories = useMemo(() => {
    const cats = ['All'];
    products.forEach((p) => {
      if (p.category && !cats.includes(p.category)) {
        cats.push(p.category);
      }
    });
    return cats;
  }, [products]);

  // Filtered products
  const filteredProducts = useMemo(() => {
    if (selectedCategory === 'All') return products;
    return products.filter((p) => p.category === selectedCategory);
  }, [products, selectedCategory]);

  const handleAddToCart = async (productId) => {
    setOperatingProductId(productId);
    try {
      const cartData = await addItemToCart(productId, 1);

      const updatedMap = {};
      cartData.items.forEach((item) => {
        updatedMap[item.product_id] = item;
      });
      setCartItemsMap(updatedMap);
      setCartCount(cartData.item_count || 0);
      toastSuccess('Product added to cart.');
    } catch (err) {
      const detail = err.response?.data?.detail || 'Failed to add product to cart.';
      toastError(detail);
    } finally {
      setOperatingProductId(null);
    }
  };

  const handleUpdateQuantity = async (productId, newQuantity) => {
    setOperatingProductId(productId);
    try {
      const cartData = await updateItemQuantity(productId, newQuantity);

      const updatedMap = {};
      cartData.items.forEach((item) => {
        updatedMap[item.product_id] = item;
      });
      setCartItemsMap(updatedMap);
      setCartCount(cartData.item_count || 0);
      toastSuccess('Cart updated.');
    } catch (err) {
      const detail = err.response?.data?.detail || 'Failed to update quantity.';
      toastError(detail);
    } finally {
      setOperatingProductId(null);
    }
  };

  const handleRemoveFromCart = async (productId) => {
    setOperatingProductId(productId);
    try {
      const cartData = await removeItemFromCart(productId);

      const updatedMap = {};
      cartData.items.forEach((item) => {
        updatedMap[item.product_id] = item;
      });
      setCartItemsMap(updatedMap);
      setCartCount(cartData.item_count || 0);
      toastSuccess('Item removed from cart.');
    } catch (err) {
      const detail = err.response?.data?.detail || 'Failed to remove item from cart.';
      toastError(detail);
    } finally {
      setOperatingProductId(null);
    }
  };

  // Skeleton placeholders during initial empty load
  if (loading && products.length === 0) {
    return (
      <div className="container">
        <div className="page-header">
          <h1 className="page-title">Products</h1>
          <p className="page-subtitle">Loading catalog products...</p>
        </div>

        <div className="skeleton-grid">
          {[1, 2, 3, 4, 5, 6, 7, 8].map((n) => (
            <div key={n} className="skeleton-card">
              <div className="skeleton-visual shimmer"></div>
              <div className="skeleton-line shimmer" style={{ width: '70%', height: '18px', marginTop: '12px' }}></div>
              <div className="skeleton-line shimmer" style={{ width: '90%', height: '14px', marginTop: '8px' }}></div>
              <div className="skeleton-line shimmer" style={{ width: '50%', height: '14px', marginTop: '6px' }}></div>
              <div className="skeleton-footer">
                <div className="skeleton-line shimmer" style={{ width: '35%', height: '20px' }}></div>
                <div className="skeleton-btn shimmer"></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  // Error state when no cached products exist
  if (products.length === 0 && loadError) {
    return (
      <div className="container">
        <div className="error-fallback-card">
          <svg className="error-fallback-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75">
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="12" />
            <line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
          <h2>Unable to Load Products</h2>
          <p>{loadError}</p>
          <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginBottom: '16px' }}>
            Free tier cloud servers go to sleep after inactivity. It might just take a moment to wake up.
          </p>
          <button className="btn-primary" onClick={() => loadData(true)}>
            Retry Loading
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '8px' }}>
        <div>
          <h1 className="page-title">Products</h1>
          <p className="page-subtitle">Browse quality workspace accessories and gear</p>
        </div>
        {isRefreshing && (
          <div className="sync-badge">
            <span className="sync-dot"></span>
            Syncing latest stock...
          </div>
        )}
      </div>

      <div className="dashboard-toolbar">
        <div className="category-filter" role="tablist" aria-label="Filter products by category">
          {categories.map((cat) => (
            <button
              key={cat}
              className={`category-chip ${selectedCategory === cat ? 'active' : ''}`}
              onClick={() => setSelectedCategory(cat)}
              role="tab"
              aria-selected={selectedCategory === cat}
            >
              {cat}
            </button>
          ))}
        </div>
        <div style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
          Showing {filteredProducts.length} product{filteredProducts.length !== 1 ? 's' : ''}
        </div>
      </div>

      <div className="product-grid">
        {filteredProducts.map((product) => (
          <ProductCard
            key={product.id}
            product={product}
            cartItem={cartItemsMap[product.id]}
            onAddToCart={handleAddToCart}
            onUpdateQuantity={handleUpdateQuantity}
            onRemoveFromCart={handleRemoveFromCart}
            isOperating={operatingProductId === product.id}
          />
        ))}
      </div>
    </div>
  );
};

export default Dashboard;

