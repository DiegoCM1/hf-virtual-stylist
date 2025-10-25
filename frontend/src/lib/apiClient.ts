// src/lib/apiClient.ts
// Uses absolute backend URL from env (Option A).
// .env.local must have: NEXT_PUBLIC_API_BASE=https://gnmicpjvt9n5dz-8000.proxy.runpod.net

const API_BASE = (process.env.NEXT_PUBLIC_API_BASE || "").replace(/\/+$/, "");
if (!API_BASE) {
  console.warn("[apiClient] NEXT_PUBLIC_API_BASE is not set");
}

type JsonInit = Omit<RequestInit, "body" | "headers"> & {
  body?: unknown;
  headers?: Record<string, string>;
  timeoutMs?: number;
};

function buildUrl(path: string) {
  const p = path.startsWith("/") ? path : `/${path}`;
  // collapse duplicate slashes without breaking protocol
  return (API_BASE + p)
    .replace(/([^:]\/)\/+/g, "$1");
}

async function withTimeout<T>(promise: Promise<T>, ms = 60000): Promise<T> {
  const ctrl = new AbortController();
  const id = setTimeout(() => ctrl.abort(), ms);
  try {
    // @ts-expect-error signal is fine to pass; caller attaches it
    const result = await promise;
    clearTimeout(id);
    return result;
  } catch (e) {
    clearTimeout(id);
    throw e;
  }
}

async function request<T>(path: string, init?: JsonInit): Promise<T> {
  const url = buildUrl(path);
  const isFormData = init?.body instanceof FormData;

  const controller = new AbortController();
  const timeoutMs = init?.timeoutMs ?? 60000;

  const res = await withTimeout(
    fetch(url, {
      ...init,
      signal: controller.signal,
      headers: {
        ...(isFormData ? {} : { "Content-Type": "application/json" }),
        ...(init?.headers || {}),
      },
      body: isFormData
        ? (init?.body as FormData)
        : init?.body !== undefined
        ? JSON.stringify(init.body)
        : undefined,
    }),
    timeoutMs
  );

  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`[apiClient] ${res.status} ${res.statusText} — ${text}`);
  }

  const ct = res.headers.get("content-type") || "";
  if (!ct.includes("application/json")) return undefined as unknown as T;
  return (await res.json()) as T;
}

/* =========================
   Generic helpers
   ========================= */
export const apiGet = <T>(path: string, init?: JsonInit) => request<T>(path, { ...init, method: "GET" });
export const apiPost = <T>(path: string, body?: unknown, init?: JsonInit) =>
  request<T>(path, { ...init, method: "POST", body });
export const apiPatch = <T>(path: string, body?: unknown, init?: JsonInit) =>
  request<T>(path, { ...init, method: "PATCH", body });
export const apiPut = <T>(path: string, body?: unknown, init?: JsonInit) =>
  request<T>(path, { ...init, method: "PUT", body });
export const apiDelete = <T>(path: string, init?: JsonInit) =>
  request<T>(path, { ...init, method: "DELETE" });

/* =========================
   Domain-specific calls
   (adjust to your backend paths)
   ========================= */

// Public catalog
export type FabricFamily = {
  id: string;
  name: string;
  preview_url?: string;
};

export const getCatalog = () => apiGet<FabricFamily[]>("/catalog");

// Generation (returns URLs or ids as your BE defines)
export type GenerateRequest = {
  prompt?: string;               // optional, depending on your flow
  fabric_id?: string;            // selected fabric/variant
  pose?: "recto" | "cruzado";    // optional if BE makes both
  // ...add any other fields your /generate expects
};

export type GenerateResponse = {
  recto_url?: string;
  cruzado_url?: string;
  // or: { images: string[] } based on your BE
};

export const generateImages = (body: GenerateRequest) =>
  apiPost<GenerateResponse>("/generate", body);
const url = `${API_BASE}${path.startsWith("/") ? path : `/${path}`}`;

// Health (optional)
export const getHealth = () => apiGet<{ status: "ok"; version?: string }>("/health");

/* =========================
   Expose base for debugging
   ========================= */
export { API_BASE };
