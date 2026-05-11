"use client";

import { useState } from "react";
import { apiRequest, setStoredToken } from "@/lib/api";
import type { TokenResponse } from "@/lib/types";

export default function RegisterPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    setMessage("Creating account...");
    try {
      const result = await apiRequest<TokenResponse>("/auth/register", {
        method: "POST",
        body: {
          email,
          password,
          location: "edmonton",
          preferred_stores: ["loblaws", "walmart", "sobeys", "save-on"],
        },
      });
      setStoredToken(result.access_token);
      window.location.href = "/onboarding";
    } catch {
      setMessage("Registration failed. Try a different email.");
    }
  }

  return (
    <main className="mx-auto flex min-h-screen max-w-md flex-col justify-center px-6">
      <h1 className="text-3xl font-semibold">Create account</h1>
      <form className="mt-6 space-y-4" onSubmit={submit}>
        <input
          className="w-full rounded-md border border-black/15 px-3 py-2"
          onChange={(event) => setEmail(event.target.value)}
          placeholder="Email"
          type="email"
          value={email}
        />
        <input
          className="w-full rounded-md border border-black/15 px-3 py-2"
          minLength={8}
          onChange={(event) => setPassword(event.target.value)}
          placeholder="Password"
          type="password"
          value={password}
        />
        <button
          className="w-full rounded-md bg-market px-4 py-2 font-semibold text-white"
          type="submit"
        >
          Create account
        </button>
      </form>
      {message ? <p className="mt-4 text-sm text-black/65">{message}</p> : null}
    </main>
  );
}
