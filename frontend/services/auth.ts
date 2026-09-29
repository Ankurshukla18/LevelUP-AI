import { api } from './api';
import { User, TokenWithUser } from '@/types';
import { getGoogleRedirectUri } from '@/lib/constants';

export const authService = {
  login: (data: { email?: string; username?: string; password: string }): Promise<TokenWithUser> =>
    api.post('/api/auth/login', data),

  register: (data: { email: string; name: string; password: string }): Promise<User> =>
    api.post('/api/auth/register', data),

  me: (): Promise<User> => api.get('/api/auth/me'),

  getGoogleAuthUrl: (redirectUri?: string): Promise<{ auth_url?: string; url?: string; is_mock?: boolean; mock?: boolean; redirect_uri?: string }> => {
    const uri = redirectUri || getGoogleRedirectUri();
    const query = uri ? `?redirect_uri=${encodeURIComponent(uri)}` : '';
    return api.get(`/api/auth/google/url${query}`);
  },

  handleGoogleCallback: (data: {
    code?: string;
    state?: string;
    redirect_uri?: string;
    mock_email?: string;
    mock_name?: string;
    mock_oauth_id?: string;
    mock_avatar?: string;
  }): Promise<TokenWithUser> => {
    const payload = {
      redirect_uri: data.redirect_uri || getGoogleRedirectUri(),
      ...data,
    };
    return api.post('/api/auth/google/callback', payload);
  },

  createFirstPassword: (data: {
    password: string;
    confirm_password?: string;
  }): Promise<TokenWithUser> => api.post('/api/auth/create-password', data),

  setPassword: (password: string): Promise<{ message: string }> =>
    api.post('/api/auth/set-password', { password }),

  verifyEmail: (token: string): Promise<{ message: string }> =>
    api.post('/api/auth/verify-email', { token }),
};
