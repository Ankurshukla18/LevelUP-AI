import { useState, useEffect, useCallback } from 'react';
import { CheckIn } from '@/types';
import { checkinsService } from '@/services/checkins';

export function useCheckins(goalId: string) {
  const [checkins, setCheckins] = useState<CheckIn[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchCheckins = useCallback(async () => {
    if (!goalId) return;
    setLoading(true);
    try {
      const data = await checkinsService.getByGoal(goalId);
      setCheckins(data);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  }, [goalId]);

  useEffect(() => {
    fetchCheckins();
  }, [fetchCheckins]);

  return { checkins, loading, refetch: fetchCheckins };
}
