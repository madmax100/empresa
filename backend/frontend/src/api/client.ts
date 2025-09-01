import axios from 'axios';

const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/contas/';
export const api = axios.create({ baseURL });

api.interceptors.response.use(
  (r) => r,
  (e) => {
    console.error('API error', e?.response?.status, e?.response?.data);
    return Promise.reject(e);
  },
);
