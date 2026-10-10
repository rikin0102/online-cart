import axios from 'axios';

const API_BASE_URL = (
  import.meta.env.VITE_API_URL ||
  (typeof window !== 'undefined' && window.localStorage?.getItem('API_URL')) ||
  'https://online-cart-lauc.onrender.com'
).replace(/\/+$/, '');

const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: 45000, // 45 seconds to accommodate free-tier cold starts
  headers: {
    'Content-Type': 'application/json',
  },
});

// Server warming state management (useful for Render free tier sleep)
const warmingListeners = new Set();
let activeRequestsCount = 0;
let warmingTimer = null;
let isWarming = false;

const notifyWarmingListeners = (warming) => {
  if (isWarming !== warming) {
    isWarming = warming;
    warmingListeners.forEach((listener) => {
      try {
        listener(warming);
      } catch (e) {
        console.error('Warming listener error:', e);
      }
    });
  }
};

export const subscribeServerWarming = (listener) => {
  warmingListeners.add(listener);
  listener(isWarming);
  return () => {
    warmingListeners.delete(listener);
  };
};

export const pingBackendHealth = async () => {
  try {
    const res = await axios.get(`${API_BASE_URL}/health`, { timeout: 8000 });
    return res.data?.status === 'ok';
  } catch {
    return false;
  }
};

// Request interceptor
client.interceptors.request.use(
  (config) => {
    // Attach authorization header if available
    const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
    if (token) {
      if (config.headers && typeof config.headers.set === 'function') {
        config.headers.set('Authorization', `Bearer ${token}`);
      } else {
        config.headers = {
          ...config.headers,
          Authorization: `Bearer ${token}`,
        };
      }
    }

    // Track active requests to detect long delays (server wake-up)
    activeRequestsCount += 1;
    if (activeRequestsCount === 1) {
      if (warmingTimer) clearTimeout(warmingTimer);
      warmingTimer = setTimeout(() => {
        if (activeRequestsCount > 0) {
          notifyWarmingListeners(true);
        }
      }, 2500); // If pending for > 2.5s, server might be waking up
    }

    return config;
  },
  (error) => {
    activeRequestsCount = Math.max(0, activeRequestsCount - 1);
    if (activeRequestsCount === 0) {
      if (warmingTimer) clearTimeout(warmingTimer);
      notifyWarmingListeners(false);
    }
    return Promise.reject(error);
  }
);

// Response interceptor: auto-retry for cold starts & handle 401s
client.interceptors.response.use(
  (response) => {
    activeRequestsCount = Math.max(0, activeRequestsCount - 1);
    if (activeRequestsCount === 0) {
      if (warmingTimer) clearTimeout(warmingTimer);
      notifyWarmingListeners(false);
    }
    return response;
  },
  async (error) => {
    const config = error.config;

    // Retry transient failures (Render wake-up returns 502/503/504 or network timeout)
    const isNetworkOr5xx =
      !error.response ||
      error.code === 'ECONNABORTED' ||
      [502, 503, 504].includes(error.response?.status);

    const isGetOrSafe = config && (config.method?.toLowerCase() === 'get' || !config.method);
    const retryCount = config?._retryCount || 0;

    if (config && isNetworkOr5xx && isGetOrSafe && retryCount < 2) {
      config._retryCount = retryCount + 1;
      const delayMs = config._retryCount * 2000; // 2s, 4s backoff
      await new Promise((resolve) => setTimeout(resolve, delayMs));
      return client(config);
    }

    activeRequestsCount = Math.max(0, activeRequestsCount - 1);
    if (activeRequestsCount === 0) {
      if (warmingTimer) clearTimeout(warmingTimer);
      notifyWarmingListeners(false);
    }

    // Response interceptor: handle 401 Unauthorized globally
    if (error.response && error.response.status === 401) {
      const currentPath = typeof window !== 'undefined' ? window.location.pathname : '';
      const url = config?.url || '';
      const isAuthEndpoint =
        url.includes('/auth/login') ||
        url.includes('/auth/register');

      if (!isAuthEndpoint && typeof window !== 'undefined') {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.dispatchEvent(new Event('auth:unauthorized'));
        if (currentPath !== '/login' && currentPath !== '/register') {
          window.location.href = '/login';
        }
      }
    }

    return Promise.reject(error);
  }
);

export default client;
