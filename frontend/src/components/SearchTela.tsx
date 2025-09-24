"use client";
import { useEffect, useMemo, useState } from "react";
import { CatalogResponse, ColorSelection } from "@/types/catalog";
import { ResolveTelaResult, SearchStatus } from "@/types/search";

type Props = {
  catalog: CatalogResponse;
  onSelect: (familyId: string, colorId: string) => void;
  resolveTelaId?: (telaId: string) => Promise<ResolveTelaResult>;
  currentFamilyId?: string;   // 👈 nuevo
  currentColorId?: string;    // 👈 nuevo
};

export default function SearchTela({
  catalog,
  onSelect,
  resolveTelaId,
  currentFamilyId,
  currentColorId,
}: Props) {
  const [value, setValue] = useState("");
  const [status, setStatus] = useState<SearchStatus>("idle");
  const [lastSearched, setLastSearched] = useState<string | null>(null);
  const [lastResolved, setLastResolved] = useState<ColorSelection | null>(null);
  const [recent, setRecent] = useState<string[]>([]);

  const colorIndex = useMemo(() => {
    const map = new Map<string, ColorSelection>();
    for (const f of catalog.families) {
      for (const c of f.colors || []) {
        map.set(c.color_id.toLowerCase(), { familyId: f.family_id, colorId: c.color_id });
      }
    }
    return map;
  }, [catalog]); // se arma desde fabrics.json (color_id p. ej. "navy-001") :contentReference[oaicite:2]{index=2}

  // 👇 Si el usuario cambia familia o color manualmente, limpiamos el banner si ya no coincide con lo último buscado
  useEffect(() => {
    if (!lastResolved) return;
    const sameFamily = currentFamilyId?.toLowerCase() === lastResolved.familyId.toLowerCase();
    const sameColor  = currentColorId?.toLowerCase() === lastResolved.colorId.toLowerCase();
    if (!sameFamily || !sameColor) {
      setStatus("idle");
      setLastResolved(null);
      setLastSearched(null);
    }
  }, [currentFamilyId, currentColorId, lastResolved]);

  async function onSearch() {
    const q = value.trim().toLowerCase();
    if (!q) return;

    // Si ya está seleccionado, muestra "already" y no cambies nada
    if (currentColorId && q === currentColorId.toLowerCase()) {
      setStatus("already");
      setLastSearched(q);
      setLastResolved(
        currentFamilyId ? { familyId: currentFamilyId, colorId: currentColorId } : null,
      );
      return;
    }

    setStatus(resolveTelaId ? "loading" : "idle");

    let hit: ColorSelection | null = null;
    if (resolveTelaId) {
      hit = await resolveTelaId(q);
    } else {
      hit = colorIndex.get(q) ?? null;
    }

    setLastSearched(q);

    if (!hit) {
      setStatus("notfound");
      setLastResolved(null);
      return;
    }

    // Si coincide con lo actualmente seleccionado
    if (currentColorId && hit.colorId.toLowerCase() === currentColorId.toLowerCase()
        && currentFamilyId && hit.familyId.toLowerCase() === currentFamilyId.toLowerCase()) {
      setStatus("already");
      setLastResolved(hit);
      return;
    }

    setStatus("ok");
    setLastResolved(hit);
    onSelect(hit.familyId, hit.colorId);

    setRecent((prev) => {
      const next = [q, ...prev.filter((x) => x !== q)];
      return next.slice(0, 3);
    });
  }

  const disabled = !value.trim() || (currentColorId && value.trim().toLowerCase() === currentColorId.toLowerCase());

  return (
    <div className="space-y-2">
      <label className="text-sm block">Search tela by ID</label>

      <div className="flex gap-2">
        <input
          className="border rounded p-2 w-full"
          placeholder="e.g. navy-001"
          value={value}
          onChange={(e) => { setValue(e.target.value); if (status !== "idle") setStatus("idle"); }}
          onKeyDown={(e) => { if (e.key === "Enter") onSearch(); }}
          aria-label="Search tela by ID"
        />
        <button
          onClick={onSearch}
          disabled={disabled || status === "loading"}
          className={`px-3 py-2 rounded text-white ${disabled || status === "loading" ? "bg-neutral-700 opacity-70" : "bg-neutral-900 hover:border hover:border-white"}`}
        >
          {status === "loading" ? "Searching…" : "Search"}
        </button>
      </div>

      <div className="min-h-[1.25rem]" aria-live="polite">
        {status === "ok" && lastResolved && (
          <p className="text-xs text-green-400">
            ✓ Found and selected — <span className="font-medium">{lastSearched}</span>
          </p>
        )}
        {status === "already" && (
          <p className="text-xs text-blue-300">
            • Already selected
          </p>
        )}
        {status === "notfound" && (
          <p className="text-xs text-red-400">ID not found.</p>
        )}
      </div>

      {recent.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {recent.map((id) => (
            <button
              key={id}
              onClick={() => { setValue(id); onSearch(); }}
              className="text-xs border rounded-full px-2 py-0.5 hover:border-white"
              title={`Search ${id}`}
            >
              {id}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
