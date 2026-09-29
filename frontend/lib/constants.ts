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

/**
 * Resolves the frontend base URL dynamically across browser and server environments:
 * 1. Client-side browser: window.location.origin (always accurate in user's browser)
 * 2. Explicit site URL: NEXT_PUBLIC_SITE_URL or NEXT_PUBLIC_APP_URL
 * 3. Vercel deployment: NEXT_PUBLIC_VERCEL_URL (e.g. *.vercel.app)
 * 4. Default fallback: http://localhost:3000
 */
export function getFrontendUrl(): string {
  if (typeof window !== "undefined" && window.location?.origin) {
    return window.location.origin;
  }
  if (process.env.NEXT_PUBLIC_SITE_URL) {
    return process.env.NEXT_PUBLIC_SITE_URL.replace(/\/$/, "");
  }
  if (process.env.NEXT_PUBLIC_APP_URL) {
    return process.env.NEXT_PUBLIC_APP_URL.replace(/\/$/, "");
  }
  if (process.env.NEXT_PUBLIC_VERCEL_URL) {
    const host = process.env.NEXT_PUBLIC_VERCEL_URL.replace(/\/$/, "");
    return host.startsWith("http") ? host : `https://${host}`;
  }
  return "http://localhost:3000";
}

/**
 * Returns the environment-aware Google OAuth callback redirect URI.
 */
export function getGoogleRedirectUri(): string {
  return `${getFrontendUrl()}/auth/callback/google`;
}

