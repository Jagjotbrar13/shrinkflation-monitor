"use client";

import Link from "next/link";

export default function OnboardingPage() {
  return (
    <main className="mx-auto flex min-h-screen max-w-2xl flex-col justify-center px-6">
      <p className="text-sm font-semibold uppercase tracking-wide text-market">Account ready</p>
      <h1 className="mt-3 text-4xl font-semibold">Start by watching products you buy often.</h1>
      <p className="mt-4 text-black/65">
        The dashboard will turn tracked product snapshots into weekly basket reports and alert
        candidates when package sizes drop.
      </p>
      <div className="mt-6 flex gap-3">
        <Link className="rounded-md bg-market px-4 py-2 text-sm font-semibold text-white" href="/">
          Browse products
        </Link>
        <Link
          className="rounded-md border border-black/15 bg-white px-4 py-2 text-sm font-semibold"
          href="/dashboard"
        >
          Open dashboard
        </Link>
      </div>
    </main>
  );
}
