import axios from 'axios'

// 로컬: Vite 프록시(/api → localhost:8000)
// 프로덕션: VITE_API_BASE_URL 환경변수에 Render 백엔드 URL 설정
const baseURL = import.meta.env.VITE_API_BASE_URL
  ? `${import.meta.env.VITE_API_BASE_URL}/api`
  : '/api'

const api = axios.create({ baseURL })

export const getDBStatus = () =>
  api.get('/lottery/status').then(r => r.data)

export const getRecentDraws = (limit = 20) =>
  api.get('/lottery/', { params: { limit } }).then(r => r.data)

export const getAllDraws = () =>
  api.get('/lottery/all').then(r => r.data)

export const getNumberStats = () =>
  api.get('/analysis/stats').then(r => r.data)

export const getReport = () =>
  api.get('/analysis/report').then(r => r.data)

export const getRecommendations = (strategy = 'balanced', count = 5) =>
  api.post('/strategy/recommend', { strategy, count }).then(r => r.data)
