"use client";

import { useEffect, useState, useCallback } from "react";
import type { FabricRead } from "@/types/admin";
import { listFabrics, setFabricStatus } from "@/lib/adminApi";
import { FabricCard, SearchBar, LuxuryButton } from "@/components/admin";

export default function AdminPage() {
  const [items, setItems] = useState<FabricRead[] | null>(null);
  const [filteredItems, setFilteredItems] = useState<FabricRead[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  // Fetch fabrics
  const fetchFabrics = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await listFabrics();
      setItems(data);
      setFilteredItems(data);
      setError(null);
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "error desconocido";
      setError(`No se pudo conectar al backend: ${msg}`);
      setItems([]);
      setFilteredItems([]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Initial load
  useEffect(() => {
    const base = process.env.NEXT_PUBLIC_API_BASE;
    if (!base) {
      setError("Backend no configurado. Define NEXT_PUBLIC_API_BASE.");
      setItems([]);
      setFilteredItems([]);
      return;
    }

    fetchFabrics();
  }, [fetchFabrics]);

  // Filter fabrics based on search
  useEffect(() => {
    if (!items) return;

    if (!searchQuery.trim()) {
      setFilteredItems(items);
      return;
    }

    const query = searchQuery.toLowerCase();
    const filtered = items.filter(
      (item) =>
        item.display_name.toLowerCase().includes(query) ||
        item.family_id.toLowerCase().includes(query) ||
        item.colors.some((c) => c.name.toLowerCase().includes(query))
    );
    setFilteredItems(filtered);
  }, [searchQuery, items]);

  // Handle status toggle
  const handleStatusToggle = async (id: number, status: "active" | "inactive") => {
    try {
      await setFabricStatus(id, status);
      // Refresh data
      await fetchFabrics();
    } catch (e) {
      console.error("Failed to toggle status:", e);
      alert("Error al cambiar el estado. Intenta de nuevo.");
    }
  };

  // Handle edit
  const handleEdit = (fabric: FabricRead) => {
    // TODO: Open edit modal
    console.log("Edit fabric:", fabric);
    alert("Función de edición próximamente");
  };

  // Handle delete
  const handleDelete = async (id: number) => {
    // TODO: Implement delete
    console.log("Delete fabric:", id);
    alert("Función de eliminación próximamente");
  };

  return (
    <main className="min-h-screen bg-gray-50 py-8 px-6">
      {/* Container */}
      <div className="max-w-[1200px] mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="font-header text-2xl tracking-[0.2em] text-gray-900 mb-2">
            FAMILIAS DE TELAS
          </h1>
          <p className="font-body text-sm text-gray-600">
            Gestiona las familias de telas y sus colores
          </p>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 rounded-[3px] border border-red-200 bg-red-50 p-4">
            <p className="font-body text-sm text-red-800">{error}</p>
          </div>
        )}

        {/* Actions Bar */}
        <div className="mb-6 flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
          {/* Search */}
          <SearchBar
            value={searchQuery}
            onChange={setSearchQuery}
            placeholder="Buscar familias, colores..."
          />

          {/* Actions */}
          <div className="flex gap-3">
            <LuxuryButton
              variant="secondary"
              size="md"
              onClick={fetchFabrics}
              disabled={isLoading}
            >
              {isLoading ? "Cargando..." : "Actualizar"}
            </LuxuryButton>
            <LuxuryButton
              variant="primary"
              size="md"
              onClick={() => alert("Función próximamente")}
            >
              + Nueva Familia
            </LuxuryButton>
          </div>
        </div>

        {/* Loading State */}
        {items === null ? (
          <div className="py-12 text-center">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
            <p className="font-body text-sm text-gray-600 mt-4">Cargando familias...</p>
          </div>
        ) : filteredItems && filteredItems.length === 0 ? (
          /* Empty State */
          <div className="py-12 text-center">
            <div className="text-gray-400 mb-4">
              <svg
                className="mx-auto h-12 w-12"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1.5}
                  d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"
                />
              </svg>
            </div>
            <p className="font-body text-gray-600">
              {searchQuery ? "No se encontraron resultados" : "No hay familias de telas"}
            </p>
            {searchQuery && (
              <button
                onClick={() => setSearchQuery("")}
                className="mt-4 font-body text-sm text-gray-900 hover:underline"
              >
                Limpiar búsqueda
              </button>
            )}
          </div>
        ) : (
          /* Fabric Cards Grid */
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredItems?.map((fabric) => (
              <FabricCard
                key={fabric.id}
                fabric={fabric}
                onStatusToggle={handleStatusToggle}
                onEdit={handleEdit}
                onDelete={handleDelete}
              />
            ))}
          </div>
        )}

        {/* Stats Footer */}
        {filteredItems && filteredItems.length > 0 && (
          <div className="mt-8 pt-6 border-t border-gray-200">
            <div className="flex items-center justify-between text-sm">
              <div className="font-body text-gray-600">
                Mostrando{" "}
                <span className="font-medium text-[var(--color-dark)]">
                  {filteredItems.length}
                </span>{" "}
                {searchQuery && items && filteredItems.length !== items.length
                  ? `de ${items.length} familias`
                  : filteredItems.length === 1
                  ? "familia"
                  : "familias"}
              </div>
              <div className="font-body text-gray-600">
                <span className="font-medium text-[var(--color-dark)]">
                  {filteredItems.reduce((sum, f) => sum + f.colors.length, 0)}
                </span>{" "}
                colores totales
              </div>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
