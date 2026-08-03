/**
 * Small fetch wrapper: attaches the JWT (stored in memory / localStorage)
 * to every request, and centralizes the base API URL. Every page imports
 * from here instead of calling fetch() directly with hardcoded URLs.
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("swe23_token");
}

export function setToken(token: string) {
  localStorage.setItem("swe23_token", token);
}

export function clearToken() {
  localStorage.removeItem("swe23_token");
}

export async function apiFetch(path: string, options: RequestInit = {}) {
  const token = getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string> | undefined),
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${API_URL}${path}`, { ...options, headers });

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed with status ${res.status}`);
  }
  return res.json();
}

/**
 * For multipart/form-data uploads (file uploads). We deliberately do NOT
 * set a Content-Type header here - the browser sets it automatically
 * for FormData, including the required multipart boundary string. Setting
 * it manually is a common mistake that silently breaks file uploads.
 */
export async function apiUpload(path: string, formData: FormData) {
  const token = getToken();
  const headers: Record<string, string> = {};
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${API_URL}${path}`, {
    method: "POST",
    headers,
    body: formData,
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed with status ${res.status}`);
  }
  return res.json();
}
