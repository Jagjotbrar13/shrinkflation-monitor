"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { BasketReport } from "@/components/BasketReport";
import { apiGet, getStoredToken } from "@/lib/api";
import type { BasketReport as BasketReportType, User, WatchlistItem } from "@/lib/types";

export default function DashboardPage() {
  const [user, setUser] = useState<User | null>(null);
  const [watchlist, setWatchlist] = useState<WatchlistItem[]>([]);
  const [report, setReport] = useState<BasketReportType | null>(null);

  useEffect(() => {
    const token = getStoredToken();
    if (!token) {
      return;
    }
    void apiGet<User>("/auth/me", token).then(setUser);
    void apiGet<WatchlistItem[]>("/watchlist", token).then(setWatchlist).catch(() => setWatchlist([]));
    void apiGet<BasketReportType>("/reports/weekly", token).then(setReport).catch(() => setReport(null));
  }, []);

  return (
    <main className="mx-auto max-w-6xl space-y-6 px-6 py-10">
      <header>
        <p className="text-sm font-medium text-market">Personal dashboard</p>
        <h1 className="mt-2 text-4xl font-semibold">
          {user ? `Welcome, ${user.email}` : "Login to track your basket"}
        </h1>
      </header>

      <BasketReport report={report} />

      <section className="rounded-lg border border-black/10 bg-white p-5">
        <div className="flex items-center justify-between gap-4">
          <h2 className="text-xl font-semibold">Watchlist</h2>
          <Link className="text-sm font-semibold text-market" href="/watchlist">
            Manage
          </Link>
        </div>
        <div className="mt-4 grid gap-3 md:grid-cols-2">
          {watchlist.map((item) => (
            <Link
              className="rounded-md border border-black/10 p-3 transition hover:bg-shelf"
              href={`/product/${item.product.id}`}
              key={item.id}
            >
              <p className="font-medium">{item.product.name}</p>
              <p className="text-sm text-black/60">{item.product.brand ?? item.product.category}</p>
            </Link>
          ))}
        </div>
      </section>
    </main>
  );
}
