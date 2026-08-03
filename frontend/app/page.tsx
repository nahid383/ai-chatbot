"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { apiFetch, setToken } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      // The backend's /auth/login endpoint uses the standard OAuth2
      // "password" flow shape (form-encoded, field name "username"
      // even though we're sending an email) - matches FastAPI/Swagger
      // conventions. This is a plain fetch (not apiFetch) because the
      // content type here is form-encoded, not JSON.
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const formBody = new URLSearchParams();
      formBody.set("username", email);
      formBody.set("password", password);

      const res = await fetch(`${apiUrl}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: formBody.toString(),
      });

      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail || "Login failed.");
      }

      const data = await res.json();
      setToken(data.access_token);

      // Ask the backend who we are, then route accordingly - admins
      // (the CR) manage content from a dashboard; students go straight
      // to chat. This keeps role logic server-side (see /auth/me).
      const me = await apiFetch("/auth/me");
      router.push(me.role === "admin" ? "/admin" : "/chat");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center px-4">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-sm rounded-xl border border-slate-200 bg-white p-8 shadow-sm"
      >
        <h1 className="mb-1 text-xl font-semibold">SWE23 AI Assistant</h1>
        <p className="mb-6 text-sm text-slate-500">
          Sign in with the account your CR created for you.
        </p>

        <label className="mb-1 block text-sm font-medium">Email</label>
        <input
          type="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="mb-4 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-slate-500"
        />

        <label className="mb-1 block text-sm font-medium">Password</label>
        <input
          type="password"
          required
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="mb-4 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-slate-500"
        />

        {error && <p className="mb-4 text-sm text-red-600">{error}</p>}

        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-lg bg-slate-900 py-2 text-sm font-medium text-white transition hover:bg-slate-700 disabled:opacity-50"
        >
          {loading ? "Signing in..." : "Sign in"}
        </button>
      </form>
    </main>
  );
}
