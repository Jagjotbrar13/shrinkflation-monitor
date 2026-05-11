"use client";

import Link from "next/link";
import { Trash2 } from "lucide-react";
import { useEffect, useState } from "react";
import { apiGet, apiRequest, getStoredToken } from "@/lib/api";
import type { WatchlistItem } from "@/lib/types";

export default function WatchlistPage() {
  const [items, setItems] = useState<WatchlistItem[]>([]);

  async function loadWatchlist() {
    const token = getStoredToken();
    if (!token) {
      return;
    }
    setItems(await apiGet<WatchlistItem[]>("/watchlist", token));
  }

  async function remove(productId: string) {
    const token = getStoredToken();
    if (!token) {
      return;
    }
    await apiRequest(`/watchlist/${productId}`, { method: "DELETE", token });
    await loadWatchlist();
  }

  useEffect(() => {
    const token = getStoredToken();
    if (token) {
      void apiGet<WatchlistItem[]>("/watchlist", token).then(setItems);
    }
  }, []);

  return (
    <main className="mx-auto max-w-4xl px-6 py-10">
      <h1 className="text-4xl font-semibold">Watchlist</h1>
      <div className="mt-6 divide-y divide-black/10 rounded-lg border border-black/10 bg-white">
        {items.map((item) => (
          <div className="flex items-center justify-between gap-4 p-4" key={item.id}>
            <Link href={`/product/${item.product.id}`}>
              <p className="font-medium">{item.product.name}</p>
              <p className="text-sm text-black/60">{item.product.brand ?? item.product.category}</p>
            </Link>
            <button
              aria-label={`Remove ${item.product.name}`}
              className="rounded-md border border-black/10 p-2 text-black/65 hover:bg-shelf"
              onClick={() => void remove(item.product.id)}
              type="button"
            >
              <Trash2 aria-hidden className="h-4 w-4" />
            </button>
          </div>
        ))}
      </div>
    </main>
  );
}
