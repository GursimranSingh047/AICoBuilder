import axios from 'axios'

// ─── Base client ─────────────────────────────────────────────────────────────
const api = axios.create({
  baseURL: 'http://127.0.0.1:8000',
  timeout: 60000,          // 60 s – generation can be slow
  headers: { 'Content-Type': 'application/json' },
})

// Attach JWT automatically
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('pp_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Unwrap error messages
api.interceptors.response.use(
  (res) => res,
  (err) => {
    const msg =
      err.response?.data?.detail ||
      err.response?.data?.message ||
      err.message ||
      'Unknown error'
    return Promise.reject(new Error(msg))
  }
)

// ─── Auth ─────────────────────────────────────────────────────────────────────
export const authAPI = {
  signup: (data) => api.post('/auth/signup', data),
  login:  (data) => api.post('/auth/login', data),
  me:     ()     => api.get('/auth/me'),
}

// ─── Projects ─────────────────────────────────────────────────────────────────
export const projectsAPI = {
  // POST /projects/generate  { idea, project_name? }
  generate: (idea, projectName = null) =>
    api.post('/projects/generate', { idea, project_name: projectName }),

  // GET /projects/
  list: (skip = 0, limit = 20) =>
    api.get('/projects/', { params: { skip, limit } }),

  // GET /projects/{id}
  get: (id) => api.get(`/projects/${id}`),

  // GET /projects/{id}/download  (returns blob)
  downloadUrl: (id) => `http://127.0.0.1:8000/projects/${id}/download`,

  // DELETE /projects/{id}
  delete: (id) => api.delete(`/projects/${id}`),
}

// ─── Chat ─────────────────────────────────────────────────────────────────────
export const chatAPI = {
  // POST /chat/  { message, project_id?, history }
  send: (message, history = [], projectId = null) =>
    api.post('/chat/', { message, history, project_id: projectId }),

  // POST /chat/improve  ?code=...&instruction=...
  improve: (code, instruction) =>
    api.post('/chat/improve', null, { params: { code, instruction } }),

  // POST /chat/explain  ?code=...
  explain: (code) =>
    api.post('/chat/explain', null, { params: { code } }),
}

// ─── Suggest (ML) ─────────────────────────────────────────────────────────────
export const suggestAPI = {
  // POST /suggest/  { idea }
  suggest: (idea) => api.post('/suggest/', { idea }),

  // GET /suggest/stacks
  stacks: () => api.get('/suggest/stacks'),

  // GET /suggest/features/{project_type}
  features: (type) => api.get(`/suggest/features/${type}`),
}

// ─── Health ───────────────────────────────────────────────────────────────────
export const healthAPI = {
  check: () => api.get('/health'),
}

export default api
