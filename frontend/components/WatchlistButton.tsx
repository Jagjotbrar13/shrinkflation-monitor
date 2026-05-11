"use client";

import { BellPlus } from "lucide-react";
import { useState } from "react";
import { apiRequest, getStoredToken } from "@/lib/api";

export function WatchlistButton({ productId }: { productId: string }) {
  const [status, setStatus] = useState<"idle" | "saving" | "saved" | "error">("idle");

  async function addToWatchlist() {
    const token = getStoredToken();
    if (!token) {
      setStatus("error");
      return;
    }
    setStatus("saving");
    try {
      await apiRequest(`/watchlist/${productId}`, { method: "POST", token });
      setStatus("saved");
    } catch {
      setStatus("error");
    }
  }

  return (
    <button
      className="inline-flex items-center gap-2 rounded-md bg-market px-4 py-2 text-sm font-semibold text-white transition hover:bg-market/90"
      onClick={addToWatchlist}
      type="button"
    >
      <BellPlus aria-hidden className="h-4 w-4" />
      {status === "saving" ? "Saving" : status === "saved" ? "Watching" : "Watch"}
    </button>
  );
}
