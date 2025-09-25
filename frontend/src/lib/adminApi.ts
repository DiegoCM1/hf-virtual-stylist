export const API = process.env.NEXT_PUBLIC_API_BASE!;

export async function listFabrics(params?: { q?: string; status?: "active" | "inactive"; limit?: number; offset?: number }) {
  const usp = new URLSearchParams();
  if (params?.q) usp.set("q", params.q);
  if (params?.status) usp.set("status_filter", params.status);
  usp.set("limit", String(params?.limit ?? 50));
  usp.set("offset", String(params?.offset ?? 0));

  const r = await fetch(`${API}/admin/fabrics?${usp.toString()}`, { cache: "no-store" });
  if (!r.ok) throw new Error(`Failed to load fabrics (${r.status})`);
  return r.json();
}

export async function createFabric(body: {
  family_id: string;
  display_name: string;
  status: "active" | "inactive";
  colors?: { color_id: string; name: string; hex_value: string; swatch_url?: string | null }[];
}) {
  const r = await fetch(`${API}/admin/fabrics`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function deactivateFabric(id: number) {
  const r = await fetch(`${API}/admin/fabrics/${id}/deactivate`, { method: "POST" });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function setFabricStatus(id: number, status: "active" | "inactive") {
  const r = await fetch(`${process.env.NEXT_PUBLIC_API_BASE}/admin/fabrics/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status }),
  });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}