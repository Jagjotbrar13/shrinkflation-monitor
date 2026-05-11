"use client";

import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ReferenceDot,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { Snapshot } from "@/lib/types";

export function PriceChart({ snapshots }: { snapshots: Snapshot[] }) {
  const data = snapshots.map((snapshot, index) => ({
    date: new Date(snapshot.scraped_at).toLocaleDateString("en-CA", {
      month: "short",
      day: "numeric",
    }),
    ppu: Number(snapshot.price_per_unit ?? 0),
    price: Number(snapshot.price),
    index,
  }));
  const latest = data.at(-1);

  return (
    <div className="h-[360px] rounded-xl border border-black/10 bg-white p-5 soft-shadow">
      <div className="mb-4 flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 className="text-lg font-semibold">Price-per-unit history</h2>
          <p className="mt-1 text-sm text-black/55">Tracked as dollars per 100g over time.</p>
        </div>
        <div className="rounded-full bg-[#eef7f1] px-3 py-1 text-sm font-semibold text-market">
          {latest ? `$${latest.ppu.toFixed(4)}/100g latest` : "No chart data"}
        </div>
      </div>
      <ResponsiveContainer height="78%" width="100%">
        <LineChart data={data} margin={{ top: 12, right: 18, bottom: 4, left: 0 }}>
          <defs>
            <linearGradient id="ppuGradient" x1="0" x2="1" y1="0" y2="0">
              <stop offset="0%" stopColor="#2f8a62" />
              <stop offset="100%" stopColor="#b42318" />
            </linearGradient>
          </defs>
          <CartesianGrid stroke="#e8ede8" strokeDasharray="4 4" vertical={false} />
          <XAxis axisLine={false} dataKey="date" tickLine={false} tickMargin={10} />
          <YAxis
            axisLine={false}
            tickFormatter={(value) => `$${Number(value).toFixed(2)}`}
            tickLine={false}
            width={58}
          />
          <Tooltip
            contentStyle={{
              borderRadius: 10,
              border: "1px solid rgba(0,0,0,0.10)",
              boxShadow: "0 12px 30px rgba(17,32,23,0.14)",
            }}
            formatter={(value, name) => [
              name === "ppu" ? `$${Number(value).toFixed(4)}/100g` : `$${Number(value).toFixed(2)}`,
              name === "ppu" ? "Price per unit" : "Shelf price",
            ]}
          />
          <Legend verticalAlign="top" height={24} />
          <Line
            activeDot={{ r: 7, stroke: "#122017", strokeWidth: 2 }}
            dataKey="ppu"
            dot={{ r: 4, strokeWidth: 2 }}
            name="Price per unit"
            stroke="url(#ppuGradient)"
            strokeWidth={3}
            type="monotone"
          />
          <Line
            dataKey="price"
            dot={false}
            name="Shelf price"
            stroke="#8a948d"
            strokeDasharray="6 6"
            strokeWidth={2}
            type="monotone"
          />
          {latest ? (
            <ReferenceDot
              fill="#b42318"
              r={6}
              stroke="#fff"
              strokeWidth={2}
              x={latest.date}
              y={latest.ppu}
            />
          ) : null}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
