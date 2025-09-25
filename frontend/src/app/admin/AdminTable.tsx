"use client";

import { useState, useTransition } from "react";
import type { FabricRead } from "@/types/admin";
import { createFabric, deactivateFabric, listFabrics } from "@/lib/adminApi";

export default function AdminTable({ initialItems }: { initialItems: FabricRead[] }) {
  const [items, setItems] = useState<FabricRead[]>(initialItems);
  const [q, setQ] = useState("");
  const [pending, start] = useTransition();
  async function refresh(query?: string) {
    const data = await listFabrics({ q: query, limit: 50 });
    setItems(data);
  }

  return (
    <div className="space-y-6">
      <div className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div className="flex w-full max-w-sm flex-col gap-1">
            <label className="text-sm font-medium text-gray-700" htmlFor="admin-search">
              Search fabrics
            </label>
            <div className="flex gap-2">
              <input
                id="admin-search"
                value={q}
                onChange={(e) => setQ(e.target.value)}
                placeholder="Family id or name"
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm shadow-sm transition focus:border-gray-900 focus:outline-none focus:ring-2 focus:ring-gray-900/20"
              />
              <button
                onClick={() => start(() => refresh(q))}
                className="whitespace-nowrap rounded-lg bg-black px-4 py-2 text-sm font-medium text-white transition hover:bg-gray-900 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-black disabled:opacity-60 disabled:hover:bg-black/90 lg:px-5 lg:py-2.5"
                disabled={pending}
              >
                {pending ? "Searching..." : "Search"}
              </button>
            </div>
          </div>
          <QuickCreate onCreate={() => start(() => refresh(q))} />
        </div>
      </div>

      <div className="overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm">
        <div className="overflow-x-auto">
          <table className="min-w-full border-collapse text-sm sm:text-base">
            <thead className="bg-gray-50">
              <tr className="text-left text-gray-600">
                <th className="px-4 py-3 font-medium">Family</th>
                <th className="px-4 py-3 font-medium">ID</th>
                <th className="px-4 py-3 font-medium">Status</th>
                <th className="px-4 py-3 font-medium">Colors</th>
                <th className="px-4 py-3 font-medium">Actions</th>
              </tr>
            </thead>
            <tbody>
              {items.map((f) => (
                <tr key={f.id} className="border-t last:border-b-0 hover:bg-gray-50/70">
                  <td className="px-4 py-3 font-medium text-gray-900">{f.display_name}</td>
                  <td className="px-4 py-3 text-gray-600">{f.family_id}</td>
                  <td className="px-4 py-3">
                    <span
                      className={`inline-flex items-center rounded-full px-2.5 py-1 text-xs font-semibold sm:text-sm ${f.status === "active" ? "bg-emerald-100 text-emerald-700" : "bg-gray-200 text-gray-700"}`}
                    >
                      {f.status}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex flex-wrap gap-3">
                      {f.colors.map((c) => (
                        <div key={c.id} className="flex items-center gap-1 rounded-full bg-gray-100 px-2 py-1 text-xs text-gray-600">
                          <span className="inline-block h-3 w-3 rounded-full border border-white shadow" style={{ background: c.hex_value }} />
                          <span className="font-medium">{c.color_id}</span>
                        </div>
                      ))}
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <button
                      onClick={() =>
                        start(async () => {
                          await deactivateFabric(f.id);
                          await refresh(q);
                        })
                      }
                      disabled={pending || f.status !== "active"}
                      className="rounded-lg bg-black px-4 py-2 text-sm font-medium text-white transition hover:bg-gray-900 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-black disabled:cursor-not-allowed disabled:bg-gray-400"
                    >
                      Deactivate
                    </button>
                  </td>
                </tr>
              ))}
              {items.length === 0 && (
                <tr>
                  <td colSpan={5} className="px-4 py-10 text-center text-sm text-gray-500 sm:text-base">
                    No fabrics found
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
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
      className="flex w-full flex-col gap-4 rounded-lg bg-gray-50 p-4 shadow-inner lg:w-auto lg:flex-1 lg:max-w-3xl"
    >
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <div className="flex flex-col gap-1">
          <label className="text-sm font-medium text-gray-700">Display name</label>
          <input
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm shadow-sm transition focus:border-gray-900 focus:outline-none focus:ring-2 focus:ring-gray-900/20"
            value={display}
            onChange={(e) => setDisplay(e.target.value)}
          />
        </div>
        <div className="flex flex-col gap-1">
          <label className="text-sm font-medium text-gray-700">Color name</label>
          <input
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm shadow-sm transition focus:border-gray-900 focus:outline-none focus:ring-2 focus:ring-gray-900/20"
            value={colorName}
            onChange={(e) => setColorName(e.target.value)}
          />
        </div>
        <div className="flex flex-col gap-1">
          <label className="text-sm font-medium text-gray-700">Hex</label>
          <input
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm shadow-sm transition focus:border-gray-900 focus:outline-none focus:ring-2 focus:ring-gray-900/20"
            value={hex}
            onChange={(e) => setHex(e.target.value)}
          />
        </div>
        <div className="flex items-end">
          <button
            type="submit"
            className="w-full rounded-lg bg-black px-4 py-2 text-sm font-medium text-white transition hover:bg-gray-900 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-black disabled:cursor-not-allowed disabled:bg-gray-400"
            disabled={pending}
          >
            {pending ? "Creating..." : "Quick Create"}
          </button>
        </div>
      </div>
    </form>
  );
}
