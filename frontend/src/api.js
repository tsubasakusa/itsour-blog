import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000/api'
})

// 自動添加 Token
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 處理 401
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.reload()
    }
    return Promise.reject(error)
  }
)

export const authAPI = {
  login: (username, password) => api.post('/auth/login', { username, password }),
  logout: () => {
    localStorage.removeItem('token')
    return Promise.resolve()
  }
}

export const articleAPI = {
  getAll: (params = {}) => api.get('/articles/', { params }),
  getOne: (id) => api.get(`/articles/${id}`),
  create: (data) => api.post('/articles/', data),
  update: (id, data) => api.put(`/articles/${id}`, data),
  delete: (id) => api.delete(`/articles/${id}`),
  search: (query) => api.get('/articles/search/query', { params: { q: query } }),
  getStats: () => api.get('/articles/stats/dashboard'),
  reindex: () => api.post('/articles/management/reindex'),
  getTags: () => api.get('/articles/tags/all'),
  getCategories: () => api.get('/articles/categories/all'),
  uploadImage: (id, file) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post(`/articles/${id}/images`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  }
}
