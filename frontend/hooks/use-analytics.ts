import { useState, useEffect, useCallback } from 'react';
import { analyticsService } from '@/services/analytics';

export function useAnalytics(goalId?: string) {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const fetchAnalytics = useCallback(async () => {
    setLoading(true);
    try {
      if (goalId) {
        const result = await analyticsService.getGoalProgress(goalId);
        setData(result);
      } else {
        const result = await analyticsService.getDashboardAnalytics();
        setData(result);
      }
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  }, [goalId]);

  useEffect(() => {
    fetchAnalytics();
  }, [fetchAnalytics]);

  return { data, loading, refetch: fetchAnalytics };
}
