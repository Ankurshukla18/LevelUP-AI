import { api } from './api';
import { User } from '@/types';

export const authService = {
  login: (data: any) => api.post('/api/auth/login', data),
  register: (data: any) => api.post('/api/auth/register', data),
  me: (): Promise<User> => api.get('/api/auth/me'),
};
