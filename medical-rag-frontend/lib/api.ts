// API configuration and helper functions
export const API_BASE_URL = "http://localhost:8000"

export async function fetchAPI(endpoint: string, options?: RequestInit) {
  try {
    const headers = {
      "Content-Type": "application/json",
      ...options?.headers,
    }

    if (options?.body instanceof FormData) {
      delete headers["Content-Type"]
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    })

    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`)
    }

    return await response.json()
  } catch (error) {
    console.error(`[v0] API fetch error for ${endpoint}:`, error)
    throw error
  }
}
