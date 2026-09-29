import { useState, useEffect, useCallback } from 'react';
import { Roadmap } from '@/types';
import { roadmapService } from '@/services/roadmap';

export function useRoadmap(goalId: string) {
  const [roadmap, setRoadmap] = useState<Roadmap | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchRoadmap = useCallback(async () => {
    if (!goalId) return;
    setLoading(true);
    try {
      const data = await roadmapService.get(goalId);
      setRoadmap(data);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  }, [goalId]);

  useEffect(() => {
    fetchRoadmap();
  }, [fetchRoadmap]);

  return { roadmap, loading, refetch: fetchRoadmap };
}
