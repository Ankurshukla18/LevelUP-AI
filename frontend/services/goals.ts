import { api } from './api';
import { Goal } from '@/types';

export const goalsService = {
  getAll: (): Promise<Goal[]> => api.get('/api/goals'),
  getById: (id: string): Promise<Goal> => api.get(`/api/goals/${id}`),
  create: (data: any): Promise<Goal> => api.post('/api/goals', data),
  update: (id: string, data: any): Promise<Goal> => api.put(`/api/goals/${id}`, data),
  delete: (id: string) => api.delete(`/api/goals/${id}`),
};
