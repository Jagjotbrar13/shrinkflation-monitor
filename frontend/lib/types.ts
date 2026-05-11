type Product = {
  id: string;
  barcode: string | null;
  name: string;
  brand: string | null;
  category: string | null;
  subcategory: string | null;
};

export type Snapshot = {
  id: string;
  product_id: string;
  store: string;
  location: string | null;
  price: string;
  weight_g: string | null;
  volume_ml: string | null;
  price_per_unit: string | null;
  unit_type: string | null;
  scraped_at: string;
};

export type ShrinkEvent = {
  id: string;
  product_id: string;
  product_name: string;
  brand: string | null;
  category: string | null;
  store: string;
  detected_at: string;
  old_weight_g: string | null;
  new_weight_g: string | null;
  old_price: string;
  new_price: string;
  old_ppu: string | null;
  new_ppu: string | null;
  ppu_change_pct: string | null;
  severity: string;
};

export type ProductDetail = Product & {
  latest_snapshots: Snapshot[];
  shrink_events: ShrinkEvent[];
};

export type Insight = {
  title: string;
  body: string;
  tone: "neutral" | "positive" | "warning";
};

export type User = {
  id: string;
  email: string;
  location: string;
  preferred_stores: string[] | null;
};

export type TokenResponse = {
  access_token: string;
  token_type: "bearer";
  user: User;
};

export type WatchlistItem = {
  id: string;
  product: Product;
  added_at: string;
};

export type BasketReport = {
  user_id: string;
  week: string;
  tracked_products: number;
  current_cost: string;
  previous_cost: string;
  change_pct: string;
  insights: Insight[];
};

export type StoreComparisonRow = {
  store: string;
  average_price_per_unit: string;
  products_tracked: number;
};
