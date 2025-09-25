"use client";

import { useRouter } from "next/navigation";
import { useState, useTransition } from "react";
import type { FabricRead } from "@/types/admin";
import { createFabric, deactivateFabric, listFabrics } from "@/lib/adminApi";

export default function AdminTable({ initialItems }: { initialItems: FabricRead[] }) {
  const [items, setItems] = useState<FabricRead[]>(initialItems);
  const [q, setQ] = useState("");
  const [pending, start] = useTransition();
  const router = useRouter();

  async function refresh(query?: string) {
    const data = await listFabrics({ q: query, limit: 50 });
    setItems(data);
  }

  return (
    <div className="space-y-3">
      <div className="flex items-end gap-3">
        <div className="flex flex-col">
          <label className="text-sm">Search</label>
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="family id or name"
            className="border rounded px-2 py-1"
          />
        </div>
        <button
          onClick={() => start(() => refresh(q))}
          className="px-3 py-2 rounded bg-black text-white"
          disabled={pending}
        >
          {pending ? "Searching..." : "Search"}
        </button>
        <QuickCreate onCreate={() => start(() => refresh(q))} />
      </div>

      <table className="w-full border-collapse">
        <thead>
          <tr className="text-left border-b">
            <th className="py-2 pr-4">Family</th>
            <th className="py-2 pr-4">ID</th>
            <th className="py-2 pr-4">Status</th>
            <th className="py-2 pr-4">Colors</th>
            <th className="py-2 pr-4">Actions</th>
          </tr>
        </thead>
        <tbody>
          {items.map((f) => (
            <tr key={f.id} className="border-b">
              <td className="py-2 pr-4">{f.display_name}</td>
              <td className="py-2 pr-4">{f.family_id}</td>
              <td className="py-2 pr-4">
                <span className={`px-2 py-1 rounded text-sm ${f.status === "active" ? "bg-green-200" : "bg-gray-300"}`}>
                  {f.status}
                </span>
              </td>
              <td className="py-2 pr-4">
                <div className="flex gap-2">
                  {f.colors.map((c) => (
                    <div key={c.id} className="flex items-center gap-1">
                      <span className="inline-block w-3 h-3 rounded" style={{ background: c.hex_value }} />
                      <span className="text-xs text-gray-600">{c.color_id}</span>
                    </div>
                  ))}
                </div>
              </td>
              <td className="py-2 pr-4">
                <button
                  onClick={() =>
                    start(async () => {
                      await deactivateFabric(f.id);
                      await refresh(q);
                    })
                  }
                  disabled={pending || f.status !== "active"}
                  className="px-3 py-1 rounded bg-black text-white disabled:opacity-50"
                >
                  Deactivate
                </button>
              </td>
            </tr>
          ))}
          {items.length === 0 && (
            <tr>
              <td colSpan={5} className="py-6 text-center text-gray-500">
                No fabrics found
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}

function QuickCreate({ onCreate }: { onCreate: () => void }) {
  const [display, setDisplay] = useState("");
  const [colorName, setColorName] = useState("");
  const [hex, setHex] = useState("#0022FF");
  const [pending, start] = useTransition();

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        start(async () => {
          await createFabric({
            family_id: `demo-${Date.now()}`,
            display_name: display || "Demo Family",
            status: "active",
            colors: [
              {
                color_id: `demo-${Math.random().toString(36).slice(2, 7)}`,
                name: colorName || "Demo",
                hex_value: hex,
              },
            ],
          });
          setDisplay("");
          setColorName("");
          onCreate();
        });
      }}
      className="flex items-end gap-2"
    >
      <div className="flex flex-col">
        <label className="text-sm">Display name</label>
        <input className="border rounded px-2 py-1" value={display} onChange={(e) => setDisplay(e.target.value)} />
      </div>
      <div className="flex flex-col">
        <label className="text-sm">Color name</label>
        <input className="border rounded px-2 py-1" value={colorName} onChange={(e) => setColorName(e.target.value)} />
      </div>
      <div className="flex flex-col">
        <label className="text-sm">Hex</label>
        <input className="border rounded px-2 py-1" value={hex} onChange={(e) => setHex(e.target.value)} />
      </div>
      <button className="px-3 py-2 rounded bg-black text-white" disabled={pending}>
        {pending ? "Creating..." : "Quick Create"}
      </button>
    </form>
  );
}
