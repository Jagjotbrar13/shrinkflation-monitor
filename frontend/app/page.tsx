"use client";

import {
  Activity,
  AlertTriangle,
  BarChart3,
  CircleDollarSign,
  Search,
  ShieldCheck,
  Store,
  TrendingUp,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { LeaderBoard } from "@/components/LeaderBoard";
import { StoreComparison } from "@/components/StoreComparison";
import { apiGet } from "@/lib/api";
import type { ShrinkEvent, StoreComparisonRow } from "@/lib/types";

export default function Home() {
  const [events, setEvents] = useState<ShrinkEvent[]>([]);
  const [stores, setStores] = useState<StoreComparisonRow[]>([]);
  const [activeStore, setActiveStore] = useState("all");
  const [query, setQuery] = useState("");

  useEffect(() => {
    void apiGet<ShrinkEvent[]>("/public/leaderboard?limit=50")
      .then(setEvents)
      .catch(() => setEvents([]));
    void apiGet<StoreComparisonRow[]>("/public/stores/comparison")
      .then(setStores)
      .catch(() => setStores([]));
  }, []);

  const filteredEvents = useMemo(() => {
    const normalized = query.toLowerCase();
    return events.filter((event) => {
      const matchesStore = activeStore === "all" || event.store === activeStore;
      if (!query.trim()) {
        return matchesStore;
      }
      const matchesQuery = [event.product_name, event.store, event.brand ?? "", event.category ?? ""]
        .join(" ")
        .toLowerCase()
        .includes(normalized);
      return matchesStore && matchesQuery;
    });
  }, [activeStore, events, query]);

  const stats = useMemo(() => {
    const criticalCount = events.filter((event) => event.severity === "critical").length;
    const averageChange =
      events.reduce((total, event) => total + Number(event.ppu_change_pct ?? 0), 0) /
      Math.max(events.length, 1);
    const categories = new Set(events.map((event) => event.category).filter(Boolean));
    return {
      events: events.length,
      criticalCount,
      averageChange: averageChange.toFixed(1),
      categories: categories.size,
    };
  }, [events]);

  const storeFilters = useMemo(
    () => ["all", ...Array.from(new Set(events.map((event) => event.store)))],
    [events],
  );

  return (
    <main className="min-h-screen bg-[#f4f7f5]">
      <section className="relative overflow-hidden border-b border-black/10 bg-[#0f1d15] text-white">
        <div className="absolute -left-24 top-10 h-72 w-72 rounded-full bg-[#2f8a62]/30 blur-3xl animate-pulse-glow" />
        <div className="absolute -right-20 bottom-0 h-80 w-80 rounded-full bg-[#d7a84f]/20 blur-3xl" />
        <div className="absolute inset-x-0 bottom-0 h-24 bg-gradient-to-t from-[#f4f7f5]/10 to-transparent" />

        <div className="relative mx-auto grid max-w-6xl gap-8 px-6 py-12 lg:grid-cols-[1fr_390px] lg:items-center">
          <div className="flex flex-col gap-7 animate-rise-in">
            <div className="flex items-center gap-3 text-[#8bd3aa]">
              <TrendingUp aria-hidden className="h-7 w-7" />
              <span className="text-sm font-semibold uppercase tracking-wide">
                Edmonton grocery intelligence
              </span>
            </div>
            <div className="max-w-3xl">
              <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-white/12 bg-white/8 px-3 py-1 text-xs font-semibold text-white/75 backdrop-blur">
                <span className="h-2 w-2 rounded-full bg-[#8bd3aa]" />
                Live demo monitoring 28 products
              </div>
              <h1 className="max-w-3xl text-4xl font-semibold leading-tight md:text-6xl">
                Grocery Shrinkflation Monitor
              </h1>
              <p className="mt-4 max-w-2xl text-lg leading-8 text-white/72">
                Spot package-size drops, compare unit-price pressure, and track which Canadian
                grocery chains are quietly making baskets more expensive.
              </p>
            </div>
            <div className="flex flex-wrap gap-3">
              <a
                className="rounded-md bg-[#2f8a62] px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:-translate-y-0.5 hover:bg-[#277552]"
                href="/login"
              >
                Login
              </a>
              <a
                className="rounded-md border border-white/20 bg-white px-4 py-2 text-sm font-semibold text-[#122017] transition hover:-translate-y-0.5 hover:bg-[#f5f7f4]"
                href="/register"
              >
                Create account
              </a>
            </div>
          </div>

          <div className="rounded-2xl border border-white/12 bg-white/10 p-4 shadow-2xl shadow-black/20 backdrop-blur-xl animate-rise-in">
            <div className="mb-4 flex items-center justify-between">
              <div>
                <p className="text-sm font-semibold text-white">Shrinkflation pulse</p>
                <p className="mt-1 text-xs text-white/55">Demo basket pressure, Edmonton focus</p>
              </div>
              <Activity aria-hidden className="h-5 w-5 text-[#8bd3aa]" />
            </div>
            <HeroTrendGraph />
            <div className="mt-4 grid grid-cols-2 gap-3">
              <MetricCard icon={<ShieldCheck className="h-4 w-4" />} label="Tracked events" value={stats.events.toString()} />
              <MetricCard icon={<TrendingUp className="h-4 w-4" />} label="Avg unit spike" value={`+${stats.averageChange}%`} />
              <MetricCard icon={<AlertTriangle className="h-4 w-4" />} label="Critical alerts" value={stats.criticalCount.toString()} />
              <MetricCard icon={<CircleDollarSign className="h-4 w-4" />} label="Categories" value={stats.categories.toString()} />
            </div>
          </div>
        </div>
      </section>

      <section className="mx-auto grid max-w-6xl gap-6 px-6 py-8 lg:grid-cols-[1fr_340px]">
        <div className="space-y-4">
          <div className="rounded-xl border border-black/10 bg-white/90 p-3 soft-shadow backdrop-blur">
            <div className="flex items-center gap-2 rounded-md bg-[#f8f7f3] px-3 py-2">
              <Search aria-hidden className="h-4 w-4 text-black/45" />
              <input
                className="w-full bg-transparent text-sm outline-none"
                onChange={(event) => setQuery(event.target.value)}
                placeholder="Filter by product, store, brand, or category"
                value={query}
              />
            </div>
            <div className="mt-3 flex flex-wrap gap-2">
              {storeFilters.map((storeName) => (
                <button
                  className={`rounded-md px-3 py-1.5 text-sm font-medium capitalize transition ${
                    activeStore === storeName
                      ? "bg-[#122017] text-white shadow-sm"
                      : "border border-black/10 bg-white text-black/70 hover:-translate-y-0.5 hover:bg-[#eef3f0]"
                  }`}
                  key={storeName}
                  onClick={() => setActiveStore(storeName)}
                  type="button"
                >
                  {storeName}
                </button>
              ))}
            </div>
          </div>
          <LeaderBoard events={filteredEvents} />
        </div>
        <aside className="space-y-4">
          <div className="rounded-xl border border-black/10 bg-white p-5 soft-shadow">
            <div className="flex items-center gap-2 text-market">
              <AlertTriangle aria-hidden className="h-5 w-5" />
              <h2 className="font-semibold">Highest risk signal</h2>
            </div>
            <p className="mt-3 text-3xl font-semibold">
              {events[0] ? `+${events[0].ppu_change_pct}%` : "+0.0%"}
            </p>
            <p className="mt-2 text-sm leading-6 text-black/65">
              {events[0] ? (
                <>
                  {events[0].product_name} at {titleCase(events[0].store)} currently has the
                  largest demo unit-price jump.
                </>
              ) : (
                "No shrinkflation events loaded yet."
              )}
            </p>
          </div>
          <div className="rounded-xl border border-black/10 bg-white p-5 shadow-sm">
            <div className="flex items-center gap-2 text-market">
              <BarChart3 aria-hidden className="h-5 w-5" />
              <h2 className="font-semibold">Portfolio-ready system</h2>
            </div>
            <p className="mt-3 text-sm leading-6 text-black/65">
              FastAPI, PostgreSQL, Redis, JWT auth, scraper pipeline, rule-based insights, reports,
              and CI/CD scaffolding.
            </p>
          </div>
          <div className="rounded-xl border border-black/10 bg-white p-5 shadow-sm">
            <div className="flex items-center gap-2 text-market">
              <Store aria-hidden className="h-5 w-5" />
              <h2 className="font-semibold">Store pressure</h2>
            </div>
            <StoreComparison rows={stores} />
          </div>
        </aside>
      </section>
    </main>
  );
}

function MetricCard({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
}) {
  return (
    <div className="rounded-xl border border-white/12 bg-white/10 p-4 shadow-sm transition hover:bg-white/14">
      <div className="flex items-center gap-2 text-[#8bd3aa]">
        {icon}
        <p className="text-xs font-medium text-white/58">{label}</p>
      </div>
      <p className="mt-2 text-3xl font-semibold text-white">{value}</p>
    </div>
  );
}

function HeroTrendGraph() {
  const bars = [34, 52, 41, 68, 58, 74, 62, 86, 78, 92, 84, 96];

  return (
    <div className="rounded-xl border border-white/10 bg-[#0b1710]/45 p-4">
      <div className="flex h-28 items-end gap-2">
        {bars.map((height, index) => (
          <div
            className="flex-1 rounded-t-md bg-gradient-to-t from-[#2f8a62] to-[#8bd3aa] opacity-90 transition hover:opacity-100"
            key={`${height}-${index}`}
            style={{ height: `${height}%` }}
          />
        ))}
      </div>
      <div className="mt-3 flex items-center justify-between text-xs text-white/50">
        <span>90 days ago</span>
        <span>Unit-price pressure trend</span>
      </div>
    </div>
  );
}

function titleCase(value: string) {
  return value.replace(/(^|\s|-)\w/g, (match) => match.toUpperCase());
}
