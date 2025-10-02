"use client";

import { useEffect, useState } from "react";
import AdminTable from "./AdminTable";
import type { FabricRead } from "@/types/admin";
import { listFabrics } from "@/lib/adminApi";

export default function AdminPage() {
  const [items, setItems] = useState<FabricRead[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const base = process.env.NEXT_PUBLIC_API_BASE_URL;
    if (!base) {
      setError("Backend caido. Define NEXT_PUBLIC_API_BASE_URL o usa rewrites en vercel.json.");
      setItems([]);
      return;
    }

    const controller = new AbortController();
    (async () => {
      try {
        const data = await listFabrics({ limit: 50 });        setItems(data);
      } catch (e: unknown) {
        const msg = e instanceof Error ? e.message : "error desconocido";
        setError(`No se pudo conectar al backend: ${msg}`);
        setItems([]);
      }
    })();

    return () => {}; // no-op
  }, []);

  return (
    <main className="p-6 space-y-4">
      <h1 className="text-2xl font-semibold">Administrador</h1>

      {error && (
        <div className="rounded border border-white/10 bg-white/5 p-4 text-sm text-red-300">
          {error}
        </div>
      )}

      {items === null ? (
        <div className="text-sm text-white/70">Cargando…</div>
      ) : (
        <AdminTable initialItems={items} />
      )}
    </main>
  );
}
