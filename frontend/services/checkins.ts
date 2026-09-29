import { api } from './api';
import { CheckIn } from '@/types';

export const checkinsService = {
  create: (goalId: string, data: any): Promise<CheckIn> => api.post(`/api/goals/${goalId}/checkins`, data),
  getByGoal: (goalId: string): Promise<CheckIn[]> => api.get(`/api/goals/${goalId}/checkins`),
};
