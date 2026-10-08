import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import client from '../api/client';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(() => localStorage.getItem('token'));
  const [cartCount, setCartCount] = useState(0);
  const [loading, setLoading] = useState(true);

  // Fetch current user and cart state
  const refreshUserData = useCallback(async () => {
    const storedToken = localStorage.getItem('token');
    if (!storedToken) {
      setUser(null);
      setCartCount(0);
      setLoading(false);
      return;
    }

    try {
      const [meRes, cartRes] = await Promise.allSettled([
        client.get('/auth/me'),
        client.get('/cart'),
      ]);

      if (meRes.status === 'fulfilled') {
        setUser(meRes.value.data);
      } else {
        // Token is invalid/expired
        localStorage.removeItem('token');
        setToken(null);
        setUser(null);
        setCartCount(0);
        setLoading(false);
        return;
      }

      if (cartRes.status === 'fulfilled') {
        setCartCount(cartRes.value.data.item_count || 0);
      }
    } catch (err) {
      console.error('Error refreshing auth data:', err);
      localStorage.removeItem('token');
      setToken(null);
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshUserData();
  }, [refreshUserData]);

  const refreshCartCount = useCallback(async () => {
    const storedToken = localStorage.getItem('token');
    if (!storedToken) {
      setCartCount(0);
      return;
    }
    try {
      const res = await client.get('/cart');
      setCartCount(res.data.item_count || 0);
    } catch (err) {
      console.error('Failed to fetch cart count:', err);
    }
  }, []);

  const login = async (email, password) => {
    const res = await client.post('/auth/login', { email, password });
    const { access_token, user: loggedUser } = res.data;
    localStorage.setItem('token', access_token);
    setToken(access_token);
    setUser(loggedUser);
    await refreshCartCount();
    return loggedUser;
  };

  const register = async (name, email, password) => {
    const res = await client.post('/auth/register', { name, email, password });
    return res.data;
  };

  const logout = () => {
    localStorage.removeItem('token');
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
