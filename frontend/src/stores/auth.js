import { reactive } from 'vue'
import api from '../api'

const state = reactive({
  user: null,
  loaded: false,
  loading: false,
  error: null
})

function setUser(user) {
  state.user = user
  state.loaded = true
}

function setError(message) {
  state.error = message
}

export async function fetchCurrentUser() {
  try {
    const response = await api.get('/api/admin/me')
    setUser(response.data.user)
    return state.user
  } catch (error) {
    setUser(null)
    return null
  }
}

export async function ensureUser() {
  if (!state.loaded) {
    await fetchCurrentUser()
  }
  return state.user
}

export async function login(credentials) {
  state.loading = true
  setError(null)
  try {
    await api.post('/api/admin/login', credentials)
    await fetchCurrentUser()
    return { success: true }
  } catch (error) {
    const message = error?.response?.data?.error || 'Ошибка авторизации'
    setError(message)
    return { success: false, message }
  } finally {
    state.loading = false
  }
}

export async function logout() {
  try {
    await api.post('/api/admin/logout')
  } finally {
    setUser(null)
  }
}

export function useAuthState() {
  return state
}
