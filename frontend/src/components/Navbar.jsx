import React from 'react';
import { Link, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useToast } from './Toast';

const Navbar = () => {
  const { user, cartCount, logout } = useAuth();
  const { toastInfo } = useToast();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    toastInfo('Logged out successfully.');
    navigate('/login');
  };

  return (
    <header className="navbar">
      <div className="navbar-container">
        <Link to={user ? "/dashboard" : "/login"} className="navbar-brand">
          <svg
            className="navbar-brand-icon"
            viewBox="0 0 24 24"
            fill="currentColor"
            aria-hidden="true"
          >
            <path d="M7 18c-1.1 0-1.99.9-1.99 2S5.9 22 7 22s2-.9 2-2-.9-2-2-2zM1 2v2h2l3.6 7.59-1.35 2.45c-.16.28-.25.61-.25.96 0 1.1.9 2 2 2h12v-2H7.42c-.14 0-.25-.11-.25-.25l.03-.12.9-1.63h7.45c.75 0 1.41-.41 1.75-1.03l3.58-6.49A1.003 1.003 0 0 0 20 4H5.21l-.94-2H1zm16 16c-1.1 0-1.99.9-1.99 2s.89 2 1.99 2 2-.9 2-2-.9-2-2-2z" />
          </svg>
          <span>Online Cart</span>
        </Link>

        {user ? (
          <nav className="navbar-nav" aria-label="Main Navigation">
            <NavLink
              to="/dashboard"
              className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
            >
              Products
            </NavLink>
            <NavLink
              to="/cart"
              className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
            >
              Cart
              {cartCount > 0 && (
                <span className="cart-badge" aria-label={`${cartCount} items in cart`}>
                  {cartCount}
                </span>
              )}
            </NavLink>
            <div className="user-section">
              <span className="user-name">{user.name}</span>
              <button
                onClick={handleLogout}
                className="btn-logout"
                title="Log out of your account"
              >
                Logout
              </button>
            </div>
          </nav>
        ) : (
          <nav className="navbar-nav">
            <NavLink
              to="/login"
              className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
            >
              Login
            </NavLink>
            <NavLink
              to="/register"
              className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
            >
              Register
            </NavLink>
          </nav>
        )}
      </div>
    </header>
  );
};

export default Navbar;
