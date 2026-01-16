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

// Public catalog (must match backend CatalogResponse type)
export type Color = {
  color_id: string;
  name: string;
  hex: string;
  swatch_url?: string | null;
};

export type FabricFamily = {
  family_id: string;
  display_name: string;
  status: "active" | "inactive";
  sort: number;
  colors: Color[];
  lora_id?: string | null;
  default_recipe?: string | null;
};

export type CatalogResponse = {
  families: FabricFamily[];
};

export const getCatalog = () => apiGet<CatalogResponse>("/catalog");

// Generation types matching backend API
export type Cut = "recto" | "cruzado";

export type GenerateRequest = {
  family_id: string;
  color_id: string;
  cuts?: Cut[];
  seed?: number;
  quality?: "preview" | "final";
  swatch_url?: string;  // Custom swatch image URL for IP-Adapter
};

export type ImageResult = {
  cut: Cut;
  url: string;
  width: number;
  height: number;
  watermark?: boolean;
  meta?: Record<string, string>;
};

export type GenerateResponse = {
  request_id: string;
  status: "completed" | "pending" | "failed";
  images: ImageResult[];
  duration_ms?: number;
  meta?: Record<string, string>;
};

export const generateImages = (body: GenerateRequest) =>
  apiPost<GenerateResponse>("/generate", body);

// Swatch upload types and function
export type SwatchUploadResponse = {
  swatch_url: string;
  filename: string;
  size_bytes: number;
};

export const uploadSwatch = async (file: File): Promise<SwatchUploadResponse> => {
  const formData = new FormData();
  formData.append("file", file);
  return apiPost<SwatchUploadResponse>("/upload-swatch", formData);
};

// Poll for job status
export const getJobStatus = (jobId: string) =>
  apiGet<GenerateResponse>(`/jobs/${jobId}`);

// Helper: Poll job until completion or failure
export async function waitForJobCompletion(
  jobId: string,
  options: { pollIntervalMs?: number; maxWaitMs?: number } = {}
): Promise<GenerateResponse> {
  const { pollIntervalMs = 2000, maxWaitMs = 300000 } = options; // 2s poll, 5min max
  const startTime = Date.now();

  while (true) {
    const response = await getJobStatus(jobId);

    if (response.status === "completed" || response.status === "failed") {
      return response;
    }

    // Check timeout
    if (Date.now() - startTime > maxWaitMs) {
      throw new Error(`Job ${jobId} timed out after ${maxWaitMs}ms`);
    }

    // Wait before next poll
    await new Promise((resolve) => setTimeout(resolve, pollIntervalMs));
  }
}

// Health (optional)
export const getHealth = () => apiGet<{ status: "ok"; version?: string }>("/health");

/* =========================
   Expose base for debugging
   ========================= */
export { API_BASE };
