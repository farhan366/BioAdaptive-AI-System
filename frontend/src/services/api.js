import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000/api/v1';

export const api = {
  getHealth: () => axios.get(`${API_BASE_URL}/health`),
  processSignals: (payload) => axios.post(`${API_BASE_URL}/signals/process`, payload),
  getDassQuestions: () => axios.get(`${API_BASE_URL}/patients/dass-questions`),
  submitDass: (payload) => axios.post(`${API_BASE_URL}/patients/dass-assessment`, payload),
  predictStage: (payload) => axios.post(`${API_BASE_URL}/predictions/predict-stage`, payload),
  getShapExplanation: (payload) => axios.post(`${API_BASE_URL}/adaptive/explain-shap`, payload),
  getMusicRecommendation: (payload) => axios.post(`${API_BASE_URL}/adaptive/recommend-music`, payload)
};

export default api;