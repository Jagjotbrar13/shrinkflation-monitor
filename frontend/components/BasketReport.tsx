"use client";

import type { BasketReport as BasketReportType } from "@/lib/types";

export function BasketReport({ report }: { report: BasketReportType | null }) {
  if (!report) {
    return (
      <section className="rounded-lg border border-black/10 bg-white p-5 text-sm text-black/65">
        Add products to your watchlist to generate a basket report.
      </section>
    );
  }

  return (
    <section className="rounded-lg border border-black/10 bg-white p-5">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="text-sm font-medium text-black/55">{report.week}</p>
          <h2 className="mt-1 text-2xl font-semibold">Weekly basket report</h2>
        </div>
        <div className="text-right">
          <p className="text-3xl font-semibold text-alert">+{report.change_pct}%</p>
          <p className="text-sm text-black/60">
            ${report.previous_cost} to ${report.current_cost}
          </p>
        </div>
      </div>
      <div className="mt-5 space-y-2">
        {report.insights.map((insight) => (
          <p className="text-sm text-black/70" key={insight.title}>
            {insight.body}
          </p>
        ))}
      </div>
    </section>
  );
}
