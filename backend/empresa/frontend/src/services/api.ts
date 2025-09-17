import axios from 'axios';

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000', // Base URL for all API calls
});

export default api;
