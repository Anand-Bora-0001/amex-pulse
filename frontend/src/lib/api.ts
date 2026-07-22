/**
 * AmEx Pulse — API Client
 * =======================
 * Axios-based HTTP client with JWT interceptors.
 */

import axios from 'axios';

const API_BASE = '/api/v1';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor — attach JWT token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('amex_pulse_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor — handle 401s
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('amex_pulse_token');
      localStorage.removeItem('amex_pulse_user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// ── Auth API ────────────────────────────────────────────────────
export const authApi = {
  login: (email: string, password: string) =>
    api.post('/auth/login', { email, password }),
  getMe: () => api.get('/auth/me'),
};

// ── Customer API ────────────────────────────────────────────────
export const customerApi = {
  list: (params?: Record<string, any>) => api.get('/customers', { params }),
  get: (id: string) => api.get(`/customers/${id}`),
  getTimeline: (id: string) => api.get(`/customers/${id}/timeline`),
};

// ── Journey API ─────────────────────────────────────────────────
export const journeyApi = {
  list: (params?: Record<string, any>) => api.get('/journeys', { params }),
  get: (id: string) => api.get(`/journeys/${id}`),
  getGraph: (id: string) => api.get(`/journeys/${id}/graph`),
};

// ── Dashboard API ───────────────────────────────────────────────
export const dashboardApi = {
  getStats: () => api.get('/dashboard/stats'),
  getKPIs: () => api.get('/dashboard/kpis'),
};

// ── Analytics API ───────────────────────────────────────────────
export const analyticsApi = {
  getFunnel: (journeyType?: string) =>
    api.get('/analytics/funnel', { params: { journey_type: journeyType } }),
  getChannels: () => api.get('/analytics/channels'),
  getHeatmap: () => api.get('/analytics/heatmap'),
};

// ── Prediction API ──────────────────────────────────────────────
export const predictionApi = {
  get: (customerId: string) => api.get(`/predictions/${customerId}`),
  run: (customerId: string, types?: string[]) =>
    api.post('/predictions/run', { customer_id: customerId, prediction_types: types }),
};

// ── Recommendation API ──────────────────────────────────────────
export const recommendationApi = {
  get: (customerId: string) => api.get(`/recommendations/${customerId}`),
  act: (id: string, action: string) =>
    api.post(`/recommendations/${id}/act`, null, { params: { action } }),
};

export default api;
