import { API_BASE } from "@/lib/api";
import { CatalogResponse, GeneratedImage } from "@/types/catalog";
import axios from "axios";

export const api = axios.create({
  baseURL: "/api", // gets rewritten to RunPod
  timeout: 25000,  // (we'll add fallback next step)
});


type GenerateRequest = {
  familyId: string;
  colorId: string;
};

type GenerateResponse = {
  images: GeneratedImage[];
};

export async function fetchCatalog(): Promise<CatalogResponse> {
  const response = await fetch(`${API_BASE}/catalog`);
  if (!response.ok) {
    throw new Error("Failed to load catalog");
  }
  return response.json();
}

export async function generateImages({
  familyId,
  colorId,
}: GenerateRequest): Promise<GenerateResponse> {
  const response = await fetch(`${API_BASE}/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      family_id: familyId,
      color_id: colorId,
      cuts: ["recto", "cruzado"],
      quality: "final",
    }),
  });

  if (!response.ok) {
    throw new Error("Failed to generate images");
  }

  return response.json();
}
