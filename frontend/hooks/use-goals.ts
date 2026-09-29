import { useState, useEffect } from 'react';
import { Goal } from '@/types';
import { goalsService } from '@/services/goals';

export function useGoals() {
  const [goals, setGoals] = useState<Goal[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchGoals = async () => {
    try {
      const data = await goalsService.getAll();
      setGoals(data);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGoals();
  }, []);

  return { goals, loading, refetch: fetchGoals };
}
