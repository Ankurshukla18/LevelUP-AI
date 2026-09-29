import { api } from './api';
import { AIAnalysis } from '@/types';

export const aiService = {
  analyzeWeek: (goalId: string, checkinId: string): Promise<AIAnalysis> => api.post(`/api/goals/${goalId}/analyze`, { checkinId }),
  adjustRoadmap: (goalId: string, analysisId: string) => api.post(`/api/goals/${goalId}/roadmap/adjust`, { analysisId }),
  monthlyReview: (goalId: string, month: string) => api.post(`/api/goals/${goalId}/monthly-review`, { month }),
};
