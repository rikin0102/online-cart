/**
 * Extracts a human-readable error message from Axios errors or backend responses.
 * Handles string details, FastAPI 422 validation array details, Network errors, and CORS errors.
 */
export const extractErrorMessage = (err, fallback = 'An unexpected error occurred. Please try again.') => {
  if (!err) return fallback;

  // 1. Check FastAPI / Backend detail field
  if (err.response?.data?.detail) {
    const detail = err.response.data.detail;
    if (typeof detail === 'string') {
      return detail;
    }
    if (Array.isArray(detail)) {
      // FastAPI 422 validation errors: array of { loc, msg, type }
      return detail
        .map((item) => {
          if (typeof item === 'string') return item;
          if (item?.msg) {
            const field = Array.isArray(item.loc) ? item.loc[item.loc.length - 1] : '';
            return field ? `${field}: ${item.msg}` : item.msg;
          }
          return JSON.stringify(item);
        })
        .join('; ');
    }
    if (typeof detail === 'object') {
      return JSON.stringify(detail);
    }
  }

  // 2. Check Backend message field
  if (err.response?.data?.message && typeof err.response.data.message === 'string') {
    return err.response.data.message;
  }

  // 3. Check HTTP status code fallback messages
  if (err.response?.status) {
    const status = err.response.status;
    if (status === 400) return err.response.data?.detail || 'Bad request. Please check your input.';
    if (status === 401) return 'Invalid credentials or session expired.';
    if (status === 403) return 'You do not have permission to perform this action.';
    if (status === 404) return 'The requested resource was not found.';
    if (status === 409) return 'Conflict: An account with these details already exists.';
    if (status === 422) return 'Validation error: Please check all required fields.';
    if (status >= 500) return 'Server error. The backend encountered a problem. Please try again later.';
  }

  // 4. Check Network / CORS errors
  if (err.message) {
    if (err.message === 'Network Error') {
      return 'Network Error: Cannot reach backend server. Please verify backend is active and CORS is configured.';
    }
    return err.message;
  }

  return fallback;
};
