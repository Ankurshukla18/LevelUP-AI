import { API_URL } from '@/lib/constants';

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

async function fetchWithAuth(endpoint: string, options: RequestInit = {}) {
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
  
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  };

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    // Only redirect to login on 401 if it's NOT an auth endpoint itself
    if (response.status === 401 && typeof window !== 'undefined') {
      if (!endpoint.startsWith('/api/auth/login') && !endpoint.startsWith('/api/auth/register')) {
        localStorage.removeItem('token');
        window.location.href = '/login';
      }
    }
    const errorData = await response.json().catch(() => ({}));
    const message = errorData.detail || errorData.message || 'Request failed';
    throw new ApiError(response.status, message);
  }

  return response.json();
}

export const api = {
  get: (endpoint: string) => fetchWithAuth(endpoint),
  post: (endpoint: string, data: any) => fetchWithAuth(endpoint, { method: 'POST', body: JSON.stringify(data) }),
  put: (endpoint: string, data: any) => fetchWithAuth(endpoint, { method: 'PUT', body: JSON.stringify(data) }),
  delete: (endpoint: string) => fetchWithAuth(endpoint, { method: 'DELETE' }),
};
