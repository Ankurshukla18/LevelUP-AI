import { api } from './api';
import { AIAnalysis } from '@/types';

export const aiService = {
  analyzeWeek: (goalId: string, checkinId: string): Promise<AIAnalysis> =>
    api.post(`/api/goals/${goalId}/analyze`, {
      checkin_id: checkinId,
      checkinId: checkinId,
    }),
  adjustRoadmap: (goalId: string, analysisId: string, roadmapId?: string) =>
    api.post(`/api/goals/${goalId}/roadmap/adjust`, {
      analysis_id: analysisId,
      analysisId: analysisId,
      roadmap_id: roadmapId,
      roadmapId: roadmapId,
    }),
  monthlyReview: (goalId: string, month?: string) =>
    api.post(`/api/goals/${goalId}/monthly-review`, { month }),
};
