// src/lib/adminApi.ts
// Frontend will call the backend directly using an absolute URL from env.
// Make sure .env.local contains:
// NEXT_PUBLIC_API_BASE=https://gnmicpjvt9n5dz-8000.proxy.runpod.net
import type {
  FabricRead,
  ColorRead,
  FabricCreate,
  ColorCreate,
  ColorUpdate,
  GenerationJobRead
} from "@/types/admin";

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

 export const setFabricStatus = async (
   id: string | number,
   status: "active" | "inactive"
 ) => {
   const API_BASE = (process.env.NEXT_PUBLIC_API_BASE || "").replace(/\/$/, "");
   const url = `${API_BASE}/admin/fabrics/${id}/status`;
   const res = await fetch(url, {
     method: "PATCH",
     headers: { "Content-Type": "application/json" },
     body: JSON.stringify({ status }),
   });
   if (!res.ok) throw new Error(await res.text());
   return res.json();
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
   Types - Export from admin types
   ========================= */
export type Fabric = FabricRead;
export type Variant = ColorRead;

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
export const listFabrics = (params?: { q?: string; limit?: number }) => {
  const query = new URLSearchParams();
  if (params?.q) query.set("q", params.q);
  if (params?.limit) query.set("limit", params.limit.toString());
  const queryString = query.toString();
  return adminGet<Fabric[]>(`/fabrics${queryString ? `?${queryString}` : ""}`);
};
export const getFabric = (id: string | number) => adminGet<Fabric>(`/fabrics/${id}`);
export const createFabric = (data: FabricCreate) =>
  adminPost<Fabric>("/fabrics", data);
export const updateFabric = (id: string | number, data: Partial<Fabric>) =>
  adminPatch<Fabric>(`/fabrics/${id}`, data);
export const deleteFabric = (id: string | number) => adminDelete<void>(`/fabrics/${id}`);

// Optional: upload a preview image for a fabric (multipart)
export const uploadFabricPreview = (id: string | number, file: File) => {
  const fd = new FormData();
  fd.append("file", file);
  return adminFetch<Fabric>(`/fabrics/${id}/preview`, {
    method: "POST",
    body: fd,
  });
};

// Colors (new color management endpoints)
export const listColors = (params?: {
  q?: string;
  family_id?: string;
  status_filter?: "active" | "inactive";
  limit?: number;
}) => {
  const query = new URLSearchParams();
  if (params?.q) query.set("q", params.q);
  if (params?.family_id) query.set("family_id", params.family_id);
  if (params?.status_filter) query.set("status_filter", params.status_filter);
  if (params?.limit) query.set("limit", params.limit.toString());
  const queryString = query.toString();
  return adminGet<ColorRead[]>(`/colors${queryString ? `?${queryString}` : ""}`);
};

export const getColor = (id: string | number) =>
  adminGet<ColorRead>(`/colors/${id}`);

export const updateColor = (id: string | number, data: ColorUpdate) =>
  adminPatch<ColorRead>(`/colors/${id}`, data);

export const setColorStatus = async (
  id: string | number,
  status: "active" | "inactive"
) => {
  const url = `${ADMIN_BASE}/colors/${id}/status`;
  const res = await fetch(url, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
};

export const moveColorToFamily = async (
  colorId: string | number,
  fabricFamilyId: number
) => {
  const url = `${ADMIN_BASE}/colors/${colorId}/move`;
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ fabric_family_id: fabricFamilyId }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
};

export const deleteColor = (id: string | number) =>
  adminDelete<void>(`/colors/${id}`);

// Generated Images / Generation Jobs
export const listGenerations = (params?: {
  family_id?: string;
  color_id?: string;
  status_filter?: "pending" | "processing" | "completed" | "failed";
  limit?: number;
}) => {
  const query = new URLSearchParams();
  if (params?.family_id) query.set("family_id", params.family_id);
  if (params?.color_id) query.set("color_id", params.color_id);
  if (params?.status_filter) query.set("status_filter", params.status_filter);
  if (params?.limit) query.set("limit", params.limit.toString());
  const queryString = query.toString();
  return adminGet<GenerationJobRead[]>(`/generations${queryString ? `?${queryString}` : ""}`);
};

export const getGenerationsByFabric = (familyId: string, colorId: string, limit = 20) => {
  return adminGet<GenerationJobRead[]>(
    `/generations/by-fabric/${familyId}/${colorId}?limit=${limit}`
  );
};

export const getGenerationStats = () =>
  adminGet<{
    total_generations: number;
    by_status: Record<string, number>;
    by_family: Array<{ family_id: string; count: number }>;
    last_24_hours: number;
  }>("/generations/stats");

export const getGeneration = (jobId: string) =>
  adminGet<GenerationJobRead>(`/generations/${jobId}`);

export const deleteGeneration = (jobId: string) =>
  adminDelete<void>(`/generations/${jobId}`);

/* =========================
   Health / Ops (optional)
   ========================= */
export const getAdminHealth = () => adminGet<{ status: "ok"; version?: string }>("/health");

/* =========================
   Export base constants (useful for logs)
   ========================= */
export { API_BASE, ADMIN_BASE };
