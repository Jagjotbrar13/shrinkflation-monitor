"use client";

import Link from "next/link";
import type { ShrinkEvent } from "@/lib/types";

export function LeaderBoard({ events }: { events: ShrinkEvent[] }) {
  return (
    <div className="overflow-hidden rounded-lg border border-black/10 bg-white shadow-sm">
      <div className="grid grid-cols-[2fr_0.8fr_1fr_0.9fr_0.8fr] border-b border-black/10 bg-[#fbfcfb] px-4 py-3 text-sm font-semibold text-black/60">
        <span>Product</span>
        <span>Store</span>
        <span>Package</span>
        <span>PPU Change</span>
        <span>Severity</span>
      </div>
      {events.map((event) => (
        <Link
          className="grid grid-cols-[2fr_0.8fr_1fr_0.9fr_0.8fr] items-center border-b border-black/5 px-4 py-4 text-sm transition hover:bg-[#eef3f0] last:border-b-0"
          href={`/product/${event.product_id}`}
          key={event.id}
        >
          <span>
            <span className="block font-semibold text-black">{event.product_name}</span>
            <span className="mt-1 block text-xs text-black/55">
              {event.brand ?? "House brand"} · {event.category ?? "Grocery"}
            </span>
          </span>
          <span className="font-medium">{titleCase(event.store)}</span>
          <span className="text-black/65">
            {event.old_weight_g ?? "?"}g → {event.new_weight_g ?? "?"}g
          </span>
          <span className="font-semibold text-alert">+{event.ppu_change_pct ?? "0"}%</span>
          <span>
            <span className={`rounded-full px-2.5 py-1 text-xs font-semibold ${severityClass(event.severity)}`}>
              {titleCase(event.severity)}
            </span>
          </span>
        </Link>
      ))}
      {events.length === 0 ? (
        <div className="px-4 py-8 text-sm text-black/60">
          No shrinkflation events yet. Seed the demo database to populate this table.
        </div>
      ) : null}
    </div>
  );
}

function titleCase(value: string) {
  return value.replace(/(^|\s|-)\w/g, (match) => match.toUpperCase());
}

function severityClass(severity: string) {
  if (severity === "critical") {
    return "bg-red-100 text-red-800";
  }
  if (severity === "high") {
    return "bg-orange-100 text-orange-800";
  }
  if (severity === "moderate") {
    return "bg-amber-100 text-amber-800";
  }
  return "bg-emerald-100 text-emerald-800";
}
