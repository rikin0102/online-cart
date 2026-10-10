import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { getCurrentUser, loginUser, registerUser, fetchCart } from '../api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(() => (typeof window !== 'undefined' ? localStorage.getItem('token') : null));
  
  // Hydrate user profile from cache immediately so UI renders in 0ms
  const [user, setUser] = useState(() => {
    try {
      const stored = typeof window !== 'undefined' ? localStorage.getItem('user') : null;
      return stored ? JSON.parse(stored) : null;
    } catch {
      return null;
    }
  });

  const [cartCount, setCartCount] = useState(() => {
    try {
      return Number(localStorage.getItem('cart_count') || 0);
    } catch {
      return 0;
    }
  });

  // Loading is only true if we have a token but NO cached user profile to display
  const [loading, setLoading] = useState(() => {
    const storedToken = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
    const storedUser = typeof window !== 'undefined' ? localStorage.getItem('user') : null;
    return Boolean(storedToken && !storedUser);
  });

  // Fetch current user and cart state in the background
  const refreshUserData = useCallback(async () => {
    const storedToken = localStorage.getItem('token');
    if (!storedToken) {
      setUser(null);
      setCartCount(0);
      setLoading(false);
      return;
    }

    try {
      const [meResult, cartResult] = await Promise.allSettled([
        getCurrentUser(),
        fetchCart(),
      ]);

      if (meResult.status === 'fulfilled') {
        const userData = meResult.value;
        setUser(userData);
        localStorage.setItem('user', JSON.stringify(userData));
      } else {
        const errorStatus = meResult.reason?.response?.status;
        // Only invalidate if explicitly unauthorized (401/403)
        if (errorStatus === 401 || errorStatus === 403) {
          localStorage.removeItem('token');
          localStorage.removeItem('user');
          localStorage.removeItem('cart_count');
          setToken(null);
          setUser(null);
          setCartCount(0);
        }
        // If it's a network timeout or Render waking up, preserve cached user!
      }

      if (cartResult.status === 'fulfilled') {
        const count = cartResult.value.item_count || 0;
        setCartCount(count);
        localStorage.setItem('cart_count', String(count));
      }
    } catch (err) {
      console.warn('Background auth refresh error:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshUserData();
  }, [refreshUserData]);

  // Listen for global 401 events dispatched by client.js
  useEffect(() => {
    const handleUnauthorized = () => {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      localStorage.removeItem('cart_count');
      setToken(null);
      setUser(null);
      setCartCount(0);
      setLoading(false);
    };

    window.addEventListener('auth:unauthorized', handleUnauthorized);
    return () => window.removeEventListener('auth:unauthorized', handleUnauthorized);
  }, []);

  const refreshCartCount = useCallback(async () => {
    const storedToken = localStorage.getItem('token');
    if (!storedToken) {
      setCartCount(0);
      return;
    }
    try {
      const data = await fetchCart();
      const count = data.item_count || 0;
      setCartCount(count);
      localStorage.setItem('cart_count', String(count));
    } catch (err) {
      console.warn('Failed to fetch cart count:', err);
    }
  }, []);

  const login = async (email, password) => {
    const data = await loginUser({ email, password });
    const { access_token, user: loggedUser } = data;
    localStorage.setItem('token', access_token);
    localStorage.setItem('user', JSON.stringify(loggedUser));
    setToken(access_token);
    setUser(loggedUser);
    setLoading(false);
    await refreshCartCount();
    return loggedUser;
  };

  const register = async (name, email, password) => {
    const data = await registerUser({ name, email, password });
    return data;
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    localStorage.removeItem('cart_count');
    localStorage.removeItem('online_cart_cached_products');
    setToken(null);
    setUser(null);
    setCartCount(0);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        cartCount,
        setCartCount,
        refreshCartCount,
        refreshUserData,
        login,
        register,
        logout,
        loading,
        isAuthenticated: !!user,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext;

