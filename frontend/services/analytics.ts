import { api } from './api';

export const analyticsService = {
  getGoalProgress: (goalId: string) => api.get(`/api/goals/${goalId}/progress`),
  getDashboardAnalytics: () => api.get('/api/dashboard/analytics'),
};
