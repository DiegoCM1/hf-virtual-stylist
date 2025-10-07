// src/lib/adminApi.ts
// Frontend will call the backend directly using an absolute URL from env.
// Make sure .env.local contains:
// NEXT_PUBLIC_API_BASE=https://gnmicpjvt9n5dz-8000.proxy.runpod.net

const API_BASE = (process.env.NEXT_PUBLIC_API_BASE || "").replace(/\/+$/, "");
if (!API_BASE) {
  // Fail fast in dev so you don't silently hit / (current domain) by mistake
  console.warn("[adminApi] NEXT_PUBLIC_API_BASE is not set");
}

const ADMIN_BASE = `${API_BASE}/admin` as const;

type JsonInit = Omit<RequestInit, "body" | "headers"> & {
  body?: unknown;
  headers?: Record<string, string>;
};

async function adminFetch<T>(path: string, init?: JsonInit): Promise<T> {
  const url =
    `${ADMIN_BASE}${path.startsWith("/") ? path : `/${path}`}`.replace(/\/{2,}/g, "/")
      // Keep protocol slashes intact:
      .replace(/^https:\//, "https://")
      .replace(/^http:\//, "http://");

  const isFormData = init?.body instanceof FormData;

  const res = await fetch(url, {
    ...init,
    headers: {
      ...(isFormData ? {} : { "Content-Type": "application/json" }),
      ...(init?.headers || {}),
    },
    body: isFormData
      ? (init?.body as FormData)
      : init?.body !== undefined
      ? JSON.stringify(init.body)
      : undefined,
  });

  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`[adminApi] ${res.status} ${res.statusText} — ${text}`);
  }
  // Allow endpoints that return empty body (204) or non-JSON
  const ct = res.headers.get("content-type") || "";
  if (!ct.includes("application/json")) return undefined as unknown as T;
  return (await res.json()) as T;
}

/* =========================
   Example Types (adjust to your BE)
   ========================= */
export type Fabric = {
  id: string;
  name: string;
  code?: string;
  family?: string;
  preview_url?: string;
  created_at?: string;
  updated_at?: string;
};

export type Variant = {
  id: string;
  fabric_id: string;
  name: string;
  color_hex?: string;
  texture_url?: string;
  created_at?: string;
  updated_at?: string;
};

/* =========================
   Generic Helpers (use these anywhere)
   ========================= */
export const adminGet = <T>(path: string) => adminFetch<T>(path);
export const adminPost = <T>(path: string, body?: unknown) =>
  adminFetch<T>(path, { method: "POST", body });
export const adminPatch = <T>(path: string, body?: unknown) =>
  adminFetch<T>(path, { method: "PATCH", body });
export const adminPut = <T>(path: string, body?: unknown) =>
  adminFetch<T>(path, { method: "PUT", body });
export const adminDelete = <T>(path: string) =>
  adminFetch<T>(path, { method: "DELETE" });

/* =========================
   Admin: Fabrics & Variants
   (Adjust paths if your router differs)
   ========================= */

// Fabrics
export const listFabrics = () => adminGet<Fabric[]>("/fabrics");
export const getFabric = (id: string) => adminGet<Fabric>(`/fabrics/${id}`);
export const createFabric = (data: Partial<Fabric>) =>
  adminPost<Fabric>("/fabrics", data);
export const updateFabric = (id: string, data: Partial<Fabric>) =>
  adminPatch<Fabric>(`/fabrics/${id}`, data);
export const deleteFabric = (id: string) => adminDelete<void>(`/fabrics/${id}`);

// Optional: upload a preview image for a fabric (multipart)
export const uploadFabricPreview = (id: string, file: File) => {
  const fd = new FormData();
  fd.append("file", file);
  return adminFetch<Fabric>(`/fabrics/${id}/preview`, {
    method: "POST",
    body: fd,
  });
};

// Variants (two common styles; keep whichever your backend supports)
export const listVariants = () => adminGet<Variant[]>("/variants");
export const listFabricVariants = (fabricId: string) =>
  adminGet<Variant[]>(`/fabrics/${fabricId}/variants`);
export const createVariant = (data: Partial<Variant>) =>
  adminPost<Variant>("/variants", data);
export const createVariantForFabric = (fabricId: string, data: Partial<Variant>) =>
  adminPost<Variant>(`/fabrics/${fabricId}/variants`, data);
export const updateVariant = (id: string, data: Partial<Variant>) =>
  adminPatch<Variant>(`/variants/${id}`, data);
export const deleteVariant = (id: string) => adminDelete<void>(`/variants/${id}`);

/* =========================
   Health / Ops (optional)
   ========================= */
export const getAdminHealth = () => adminGet<{ status: "ok"; version?: string }>("/health");

/* =========================
   Export base constants (useful for logs)
   ========================= */
export { API_BASE, ADMIN_BASE };
