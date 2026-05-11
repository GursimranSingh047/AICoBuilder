/**
 * API Configuration
 * Centralized API URL management using environment variables
 */

// Get API URL from environment variable or use default
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Helper function to create authenticated fetch headers
export const getAuthHeaders = (token) => ({
  'Authorization': token ? `Bearer ${token}` : '',
  'Content-Type': 'application/json'
})

// Export for use in components
export default {
  baseURL: API_BASE_URL,
  getAuthHeaders
}
