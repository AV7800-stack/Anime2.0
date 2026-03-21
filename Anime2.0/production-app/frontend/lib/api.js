import axios from 'axios';

// Get API URL from environment
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Create axios instance
const api = axios.create({
  baseURL: API_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Handle 401 unauthorized
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API calls
export const authAPI = {
  register: async (userData) => {
    const response = await api.post('/api/auth/register', userData);
    return response.data;
  },
  
  login: async (credentials) => {
    const response = await api.post('/api/auth/login', credentials);
    return response.data;
  },
  
  getProfile: async () => {
    const response = await api.get('/api/auth/me');
    return response.data;
  },
  
  updateProfile: async (profileData) => {
    const response = await api.put('/api/auth/profile', profileData);
    return response.data;
  },
  
  logout: async () => {
    const response = await api.post('/api/auth/logout');
    return response.data;
  },
};

// Data API calls
export const dataAPI = {
  getAll: async (params = {}) => {
    const response = await api.get('/api/data', { params });
    return response.data;
  },
  
  getById: async (id) => {
    const response = await api.get(`/api/data/${id}`);
    return response.data;
  },
  
  create: async (data) => {
    const response = await api.post('/api/data', data);
    return response.data;
  },
  
  update: async (id, data) => {
    const response = await api.put(`/api/data/${id}`, data);
    return response.data;
  },
  
  delete: async (id) => {
    const response = await api.delete(`/api/data/${id}`);
    return response.data;
  },
  
  like: async (id) => {
    const response = await api.post(`/api/data/${id}/like`);
    return response.data;
  },
  
  getCategories: async () => {
    const response = await api.get('/api/data/categories/all');
    return response.data;
  },
};

// User API calls
export const userAPI = {
  getAll: async (params = {}) => {
    const response = await api.get('/api/users', { params });
    return response.data;
  },
  
  getById: async (id) => {
    const response = await api.get(`/api/users/${id}`);
    return response.data;
  },
  
  search: async (query) => {
    const response = await api.get('/api/users/search', { params: { q: query } });
    return response.data;
  },
  
  update: async (id, data) => {
    const response = await api.put(`/api/users/${id}`, data);
    return response.data;
  },
  
  getStats: async () => {
    const response = await api.get('/api/users/stats');
    return response.data;
  },
};

// Health check
export const healthAPI = {
  check: async () => {
    const response = await api.get('/');
    return response.data;
  },
};

export default api;
