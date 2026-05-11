"use client";

import { ArrowUpRight, BadgeAlert, PackageMinus, Store } from "lucide-react";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { InsightCard } from "@/components/InsightCard";
import { PriceChart } from "@/components/PriceChart";
import { WatchlistButton } from "@/components/WatchlistButton";
import { apiGet } from "@/lib/api";
import type { Insight, ProductDetail, Snapshot } from "@/lib/types";

export default function ProductPage() {
  const params = useParams<{ id: string }>();
  const [product, setProduct] = useState<ProductDetail | null>(null);
  const [history, setHistory] = useState<Snapshot[]>([]);
  const [insights, setInsights] = useState<Insight[]>([]);

  useEffect(() => {
    if (!params.id) {
      return;
    }
    void apiGet<ProductDetail>(`/products/${params.id}`).then(setProduct).catch(() => setProduct(null));
    void apiGet<Snapshot[]>(`/products/${params.id}/history`).then(setHistory).catch(() => setHistory([]));
    void apiGet<Insight[]>(`/insights/product/${params.id}`).then(setInsights).catch(() => setInsights([]));
  }, [params.id]);

  if (!product) {
    return (
      <main className="min-h-screen bg-[#f4f7f5]">
        <div className="mx-auto max-w-6xl px-6 py-10">Loading product...</div>
      </main>
    );
  }

  const latestEvent = product.shrink_events[0];
  const latestSnapshot = history.at(-1);
  const previousSnapshot = history.at(-2);
  const ppuDelta = latestEvent?.ppu_change_pct ?? "0.00";

  return (
    <main className="min-h-screen bg-[#f4f7f5]">
      <section className="border-b border-black/10 bg-[#101d15] text-white">
        <div className="mx-auto max-w-6xl px-6 py-10">
          <div className="flex flex-wrap items-start justify-between gap-5">
            <div>
              <p className="text-sm font-semibold uppercase tracking-wide text-[#8bd3aa]">
                {product.brand ?? product.category}
              </p>
              <h1 className="mt-3 max-w-3xl text-4xl font-semibold md:text-5xl">{product.name}</h1>
              <p className="mt-3 text-white/60">
                {product.category} · {product.subcategory ?? "Tracked product"} · Edmonton demo
              </p>
            </div>
            <WatchlistButton productId={product.id} />
          </div>

          <div className="mt-8 grid gap-3 md:grid-cols-4">
            <Metric icon={<ArrowUpRight className="h-4 w-4" />} label="Unit-price jump" value={`+${ppuDelta}%`} />
            <Metric
              icon={<PackageMinus className="h-4 w-4" />}
              label="Package change"
              value={
                latestEvent
                  ? `${latestEvent.old_weight_g}g → ${latestEvent.new_weight_g}g`
                  : "No change"
              }
            />
            <Metric
              icon={<Store className="h-4 w-4" />}
              label="Tracked store"
              value={latestEvent ? titleCase(latestEvent.store) : "Demo"}
            />
            <Metric
              icon={<BadgeAlert className="h-4 w-4" />}
              label="Severity"
              value={latestEvent ? titleCase(latestEvent.severity) : "None"}
            />
          </div>
        </div>
      </section>

      <section className="mx-auto grid max-w-6xl gap-6 px-6 py-8 lg:grid-cols-[1fr_330px]">
        <div className="space-y-6">
          <PriceChart snapshots={history} />

          <section className="grid gap-4 md:grid-cols-2">
            {insights.map((insight) => (
              <InsightCard body={insight.body} key={insight.title} title={insight.title} />
            ))}
          </section>
        </div>

        <aside className="space-y-4">
          <div className="rounded-xl border border-black/10 bg-white p-5 soft-shadow">
            <h2 className="font-semibold">Snapshot comparison</h2>
            <div className="mt-4 space-y-4 text-sm">
              <ComparisonRow
                label="Previous shelf price"
                value={previousSnapshot ? `$${Number(previousSnapshot.price).toFixed(2)}` : "n/a"}
              />
              <ComparisonRow
                label="Latest shelf price"
                value={latestSnapshot ? `$${Number(latestSnapshot.price).toFixed(2)}` : "n/a"}
              />
              <ComparisonRow
                label="Previous unit price"
                value={
                  previousSnapshot
                    ? `$${Number(previousSnapshot.price_per_unit).toFixed(4)}/100g`
                    : "n/a"
                }
              />
              <ComparisonRow
                label="Latest unit price"
                value={
                  latestSnapshot ? `$${Number(latestSnapshot.price_per_unit).toFixed(4)}/100g` : "n/a"
                }
              />
            </div>
          </div>

          <div className="rounded-xl border border-black/10 bg-white p-5 shadow-sm">
            <h2 className="font-semibold">Why it was flagged</h2>
            <p className="mt-3 text-sm leading-6 text-black/65">
              The detector compares package weight, shelf price, and price per 100g. This item was
              flagged because the package got smaller while the effective unit price increased.
            </p>
          </div>
        </aside>
      </section>
    </main>
  );
}

function Metric({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
  return (
    <div className="rounded-xl border border-white/12 bg-white/10 p-4 backdrop-blur">
      <div className="flex items-center gap-2 text-[#8bd3aa]">
        {icon}
        <p className="text-xs font-medium text-white/58">{label}</p>
      </div>
      <p className="mt-2 text-xl font-semibold text-white">{value}</p>
    </div>
  );
}

function ComparisonRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between gap-4 border-b border-black/8 pb-3 last:border-0 last:pb-0">
      <span className="text-black/58">{label}</span>
      <span className="font-semibold">{value}</span>
    </div>
  );
}

function titleCase(value: string) {
  return value.replace(/(^|\s|-)\w/g, (match) => match.toUpperCase());
}
