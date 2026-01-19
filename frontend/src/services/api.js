import axios from 'axios';

// ✅ FastAPI runs on 8000
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// --------------------
// Request interceptor
// --------------------
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// --------------------
// Response interceptor
// --------------------
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// --------------------
// Auth API
// --------------------
export const authAPI = {
  signup: (data) => api.post('/api/auth/signup', data),
  login: (data) => api.post('/api/auth/login', data),
};

// --------------------
// Dashboard API
// --------------------
export const dashboardAPI = {
  getDashboard: () => api.get('/api/dashboard/'),
};

// --------------------
// Transactions API
// --------------------
export const transactionsAPI = {
  getAll: () => api.get('/api/transactions/'),
  add: (data) => api.post('/api/transactions/add', data),
  addFromSMS: (data) => api.post('/api/transactions/from-sms', data),
  delete: (id) => api.delete(`/api/transactions/${id}`),

  // ✅ REQUIRED FOR CATEGORY CONFIRMATION
  updateCategory: (id, data) =>
    api.put(`/api/transactions/${id}/category`, data),
};

// --------------------
// Analytics API
// --------------------
export const analyticsAPI = {
  getAnalytics: (period = 'monthly') =>
    api.get(`/api/analytics/?period=${period}`),
};

// --------------------
// Profile API
// --------------------
export const profileAPI = {
  get: () => api.get('/api/profile/'),
  update: (data) => api.put('/api/profile/', data),
};

// --------------------
// AI Feedback API
// --------------------
export const feedbackAPI = {
  submit: (data) => api.post('/api/feedback/', data),
};

export default api;
