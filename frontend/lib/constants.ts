export const CATEGORIES = [
  "Academics",
  "Coding",
  "Fitness",
  "Career",
  "Personal Development",
  "Other"
] as const;

export const PRIORITIES = [
  "Low",
  "Medium",
  "High"
] as const;

export const DIFFICULTY_LEVELS = [
  "Easy",
  "Moderate",
  "Hard",
  "Very Hard"
] as const;

export const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
export const CONTACT_EMAIL = process.env.NEXT_PUBLIC_CONTACT_EMAIL || "ankuromshukla161@gmail.com";
