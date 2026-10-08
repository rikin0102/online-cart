import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { getCurrentUser, loginUser, registerUser, fetchCart } from '../api';

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
      const [meData, cartData] = await Promise.allSettled([
        getCurrentUser(),
        fetchCart(),
      ]);

      if (meData.status === 'fulfilled') {
        setUser(meData.value);
      } else {
        localStorage.removeItem('token');
        setToken(null);
        setUser(null);
        setCartCount(0);
        setLoading(false);
        return;
      }

      if (cartData.status === 'fulfilled') {
        setCartCount(cartData.value.item_count || 0);
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
      const data = await fetchCart();
      setCartCount(data.item_count || 0);
    } catch (err) {
      console.error('Failed to fetch cart count:', err);
    }
  }, []);

  const login = async (email, password) => {
    const data = await loginUser({ email, password });
    const { access_token, user: loggedUser } = data;
    localStorage.setItem('token', access_token);
    setToken(access_token);
    setUser(loggedUser);
    await refreshCartCount();
    return loggedUser;
  };

  const register = async (name, email, password) => {
    const data = await registerUser({ name, email, password });
    return data;
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
