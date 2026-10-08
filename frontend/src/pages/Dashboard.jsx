import React, { useState, useEffect, useCallback, useMemo } from 'react';
import {
  fetchProducts,
  fetchCart,
  addItemToCart,
  updateItemQuantity,
  removeItemFromCart,
} from '../api';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../components/Toast';
import ProductCard from '../components/ProductCard';
import '../styles/dashboard.css';

const Dashboard = () => {
  const [products, setProducts] = useState([]);
  const [cartItemsMap, setCartItemsMap] = useState({});
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [loading, setLoading] = useState(true);
  const [operatingProductId, setOperatingProductId] = useState(null);

  const { setCartCount } = useAuth();
  const { toastSuccess, toastError } = useToast();

  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      const [productsData, cartData] = await Promise.all([
        fetchProducts(),
        fetchCart(),
      ]);

      setProducts(productsData);

      const itemsMap = {};
      cartData.items.forEach((item) => {
        itemsMap[item.product_id] = item;
      });
      setCartItemsMap(itemsMap);
      setCartCount(cartData.item_count || 0);
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
      toastError('Could not load products. Please check your network connection.');
    } finally {
      setLoading(false);
    }
  }, [setCartCount, toastError]);

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

  if (loading) {
    return (
      <div className="container">
        <div className="loading-center">
          <div className="spinner"></div>
          <p>Loading catalog products...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <div className="page-header">
        <h1 className="page-title">Products</h1>
        <p className="page-subtitle">Browse quality workspace accessories and gear</p>
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
