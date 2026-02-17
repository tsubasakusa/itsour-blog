import axios from 'axios'

const api = axios.create({
  baseURL: '/api'
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
      if (window.location.pathname.startsWith('/plague')) {
        window.location.href = '/plague/login'
      }
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
  getBySlug: (slug) => api.get(`/articles/by-slug/${slug}`),
  create: (data) => api.post('/articles/', data),
  update: (id, data) => api.put(`/articles/${id}`, data),
  delete: (id) => api.delete(`/articles/${id}`),
  search: (query) => api.get('/articles/search/query', { params: { q: query } }),
  getStats: () => api.get('/articles/stats/dashboard'),
  reindex: () => api.post('/articles/management/reindex'),
  getTags: () => api.get('/articles/tags/all'),
  getCategories: () => api.get('/articles/categories/all'),
  getRelated: (id) => api.get(`/articles/${id}/related`),
  uploadImage: (id, file) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post(`/articles/${id}/images`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  }
}

export const categoryAPI = {
  getAll: () => api.get('/categories/'),
  create: (data) => api.post('/categories/', data),
  update: (id, data) => api.put(`/categories/${id}`, data),
  delete: (id) => api.delete(`/categories/${id}`),
}

export const mediaAPI = {
  upload: (file, altText) => {
    const formData = new FormData()
    formData.append('file', file)
    if (altText) formData.append('alt_text', altText)
    return api.post('/media/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  getAll: (params = {}) => api.get('/media/', { params }),
  getOne: (id) => api.get(`/media/${id}`),
  delete: (id) => api.delete(`/media/${id}`),
}

export const aiAPI = {
  generateSummary: (content, title) => api.post('/ai/generate-summary', { content, title }),
}

export const settingsAPI = {
  getAll: () => api.get('/settings/'),
  update: (settings) => api.put('/settings/', settings),
}
