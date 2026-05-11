"use client";

import type { StoreComparisonRow } from "@/lib/types";

export function StoreComparison({ rows }: { rows: StoreComparisonRow[] }) {
  const maxCount = Math.max(...rows.map((row) => row.products_tracked), 1);

  return (
    <div className="mt-4 space-y-4">
        {rows.map((row) => (
          <div className="space-y-2 text-sm" key={row.store}>
            <div className="flex items-center justify-between gap-4">
              <span className="font-semibold capitalize">{row.store}</span>
              <span className="text-black/60">{row.products_tracked} products</span>
            </div>
            <div className="h-2 overflow-hidden rounded-full bg-black/8">
              <div
                className="h-full rounded-full bg-market"
                style={{ width: `${Math.max(18, (row.products_tracked / maxCount) * 100)}%` }}
              />
            </div>
            <p className="text-xs text-black/55">${row.average_price_per_unit}/100g avg unit price</p>
          </div>
        ))}
        {rows.length === 0 ? <p className="text-sm text-black/60">No store data yet.</p> : null}
    </div>
  );
}
