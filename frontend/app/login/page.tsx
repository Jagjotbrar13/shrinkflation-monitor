"use client";

import { useState } from "react";
import { apiRequest, setStoredToken } from "@/lib/api";
import type { TokenResponse } from "@/lib/types";

export default function LoginPage() {
  const [email, setEmail] = useState("demo@grocerydemo.com");
  const [password, setPassword] = useState("password123");
  const [message, setMessage] = useState("");

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    setMessage("Signing in...");
    try {
      const result = await apiRequest<TokenResponse>("/auth/login", {
        method: "POST",
        body: { email, password },
      });
      setStoredToken(result.access_token);
      window.location.href = "/dashboard";
    } catch {
      setMessage("Login failed. Check your credentials.");
    }
  }

  return (
    <AuthShell
      buttonLabel="Login"
      email={email}
      message={message}
      password={password}
      setEmail={setEmail}
      setPassword={setPassword}
      submit={submit}
      title="Login"
    />
  );
}

function AuthShell(props: {
  title: string;
  buttonLabel: string;
  email: string;
  password: string;
  message: string;
  setEmail: (value: string) => void;
  setPassword: (value: string) => void;
  submit: (event: React.FormEvent) => void;
}) {
  return (
    <main className="mx-auto flex min-h-screen max-w-md flex-col justify-center px-6">
      <h1 className="text-3xl font-semibold">{props.title}</h1>
      <p className="mt-3 rounded-lg border border-black/10 bg-shelf p-3 text-sm text-black/70">
        Demo account: <strong>demo@grocerydemo.com</strong> / <strong>password123</strong>
      </p>
      <form className="mt-6 space-y-4" onSubmit={props.submit}>
        <input
          className="w-full rounded-md border border-black/15 px-3 py-2"
          onChange={(event) => props.setEmail(event.target.value)}
          placeholder="Email"
          type="email"
          value={props.email}
        />
        <input
          className="w-full rounded-md border border-black/15 px-3 py-2"
          onChange={(event) => props.setPassword(event.target.value)}
          placeholder="Password"
          type="password"
          value={props.password}
        />
        <button className="w-full rounded-md bg-market px-4 py-2 font-semibold text-white" type="submit">
          {props.buttonLabel}
        </button>
      </form>
      {props.message ? <p className="mt-4 text-sm text-black/65">{props.message}</p> : null}
    </main>
  );
}
