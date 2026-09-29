import { api } from './api';
import { Roadmap, Task } from '@/types';

export const roadmapService = {
  generate: (goalId: string): Promise<Roadmap> => api.post(`/api/goals/${goalId}/roadmap/generate`, {}),
  get: (goalId: string): Promise<Roadmap> => api.get(`/api/goals/${goalId}/roadmap`),
  updateTask: (taskId: string, data: any): Promise<Task> => api.put(`/api/roadmap/tasks/${taskId}`, data),
  deleteTask: (taskId: string) => api.delete(`/api/roadmap/tasks/${taskId}`),
  createTask: (weekId: string, data: any): Promise<Task> => api.post(`/api/roadmap/tasks/${weekId}`, data),
};
