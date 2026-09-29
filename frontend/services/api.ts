import { API_URL } from '@/lib/constants';

export class ApiError extends Error {
  constructor(public status: number, message: string, public details?: any) {
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
      if (!endpoint.startsWith('/api/auth/')) {
        localStorage.removeItem('token');
        window.location.href = '/login';
      }
    }
    const errorData = await response.json().catch(() => ({}));
    let message = errorData.detail || errorData.message || 'Request failed';
    if (Array.isArray(message)) {
      message = message
        .map((item: any) => {
          if (typeof item === 'string') return item;
          const field = Array.isArray(item.loc) ? item.loc.slice(1).join('.') : '';
          return field ? `${field}: ${item.msg || 'invalid'}` : (item.msg || JSON.stringify(item));
        })
        .join('; ');
    } else if (typeof message === 'object' && message !== null) {
      message = JSON.stringify(message);
    }
    throw new ApiError(response.status, String(message), errorData);
  }

  return response.json();
}

export const api = {
  get: (endpoint: string) => fetchWithAuth(endpoint),
  post: (endpoint: string, data: any) => fetchWithAuth(endpoint, { method: 'POST', body: JSON.stringify(data) }),
  put: (endpoint: string, data: any) => fetchWithAuth(endpoint, { method: 'PUT', body: JSON.stringify(data) }),
  delete: (endpoint: string) => fetchWithAuth(endpoint, { method: 'DELETE' }),
};
