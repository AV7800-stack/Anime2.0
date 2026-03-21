// Auth utilities
export const authUtils = {
  // Get token from localStorage
  getToken: () => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('token');
    }
    return null;
  },
  
  // Set token in localStorage
  setToken: (token) => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('token', token);
    }
  },
  
  // Remove token from localStorage
  removeToken: () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('token');
    }
  },
  
  // Get user from localStorage
  getUser: () => {
    if (typeof window !== 'undefined') {
      const user = localStorage.getItem('user');
      return user ? JSON.parse(user) : null;
    }
    return null;
  },
  
  // Set user in localStorage
  setUser: (user) => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('user', JSON.stringify(user));
    }
  },
  
  // Remove user from localStorage
  removeUser: () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('user');
    }
  },
  
  // Check if user is authenticated
  isAuthenticated: () => {
    const token = authUtils.getToken();
    const user = authUtils.getUser();
    return !!(token && user);
  },
  
  // Get user role
  getUserRole: () => {
    const user = authUtils.getUser();
    return user?.role || 'user';
  },
  
  // Check if user is admin
  isAdmin: () => {
    return authUtils.getUserRole() === 'admin';
  },
  
  // Logout user
  logout: () => {
    authUtils.removeToken();
    authUtils.removeUser();
    if (typeof window !== 'undefined') {
      window.location.href = '/login';
    }
  },
  
  // Validate email
  validateEmail: (email) => {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
  },
  
  // Validate password
  validatePassword: (password) => {
    return password && password.length >= 6;
  },
  
  // Format error message
  formatError: (error) => {
    if (error?.response?.data?.message) {
      return error.response.data.message;
    }
    if (error?.response?.data?.errors) {
      return error.response.data.errors.join(', ');
    }
    return 'An error occurred. Please try again.';
  },
};
