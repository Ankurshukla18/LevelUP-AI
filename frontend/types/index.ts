export interface User {
  id: string;
  email: string;
  name: string;
  avatar_url?: string;
  oauth_provider?: string;
  is_verified?: boolean;
  has_password?: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface TokenWithUser {
  access_token: string;
  token_type: string;
  requires_password_setup: boolean;
  user: User;
}

export interface Goal {
  id: string;
  name: string;
  category: string;
  description?: string;
  startDate: string;
  targetDate: string;
  currentLevel: string;
  targetOutcome: string;
  availableHoursPerWeek: number;
  priority: string;
  motivation?: string;
  preferredDays?: string[];
  progress: number;
  status: 'not_started' | 'in_progress' | 'completed' | 'delayed';
}

export interface Task {
  id: string;
  title: string;
  completed: boolean;
  estimatedHours: number;
}

export interface WeekPlan {
  id: string;
  weekNumber: number;
  startDate: string;
  endDate: string;
  title: string;
  tasks: Task[];
  status: 'not_started' | 'in_progress' | 'completed' | 'delayed';
}

export interface Roadmap {
  id: string;
  goalId: string;
  weeks: WeekPlan[];
}

export interface CheckIn {
  id: string;
  goalId: string;
  weekId: string;
  date: string;
  hoursSpent: number;
  accomplished: string;
  problemsFaced: string;
  difficultyLevel: string;
  selfRating: number;
  notes?: string;
}

export interface AIAnalysis {
  summary: string;
  wentWell: string[];
  delayed: string[];
  reasons: string[];
  recommendations: string[];
  nextWeekFocus: string;
  hasAdjustment: boolean;
}
