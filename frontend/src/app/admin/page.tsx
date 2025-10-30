"use client";

import { useEffect, useState, useCallback, useMemo } from "react";
import type { FabricRead } from "@/types/admin";
import { listFabrics, setFabricStatus, moveColorToFamily } from "@/lib/adminApi";
import { FabricCard, SearchBar, LuxuryButton, BulkActionBar, FilterPanel } from "@/components/admin";
import type { FilterOptions } from "@/components/admin/FilterPanel";

export default function AdminPage() {
  const [items, setItems] = useState<FabricRead[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  // Selection state
  const [isSelectionMode, setIsSelectionMode] = useState(false);
  const [selectedIds, setSelectedIds] = useState<Set<number>>(new Set());

  // Filter state
  const [filters, setFilters] = useState<FilterOptions>({
    status: "all",
    sortBy: "name",
    sortOrder: "asc",
  });

  // Fetch fabrics
  const fetchFabrics = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await listFabrics();
      setItems(data);
      setError(null);
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "error desconocido";
      setError(`No se pudo conectar al backend: ${msg}`);
      setItems([]);
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
      return;
    }

    fetchFabrics();
  }, [fetchFabrics]);

  // Filter, sort, and search fabrics
  const filteredItems = useMemo(() => {
    if (!items) return null;

    let result = [...items];

    // Apply status filter
    if (filters.status !== "all") {
      result = result.filter((item) => item.status === filters.status);
    }

    // Apply search filter
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      result = result.filter(
        (item) =>
          item.display_name.toLowerCase().includes(query) ||
          item.family_id.toLowerCase().includes(query) ||
          item.colors.some((c) => c.name.toLowerCase().includes(query))
      );
    }

    // Apply sorting
    result.sort((a, b) => {
      let comparison = 0;

      switch (filters.sortBy) {
        case "name":
          comparison = a.display_name.localeCompare(b.display_name);
          break;
        case "created":
          comparison =
            new Date(a.created_at || 0).getTime() -
            new Date(b.created_at || 0).getTime();
          break;
        case "colors":
          comparison = a.colors.length - b.colors.length;
          break;
        case "recent":
          comparison =
            new Date(a.updated_at || 0).getTime() -
            new Date(b.updated_at || 0).getTime();
          break;
      }

      return filters.sortOrder === "asc" ? comparison : -comparison;
    });

    return result;
  }, [items, searchQuery, filters]);

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

  // Selection handlers
  const handleToggleSelection = (id: number) => {
    setSelectedIds((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(id)) {
        newSet.delete(id);
      } else {
        newSet.add(id);
      }
      return newSet;
    });
  };

  const handleSelectAll = () => {
    if (filteredItems) {
      setSelectedIds(new Set(filteredItems.map((item) => item.id)));
    }
  };

  const handleDeselectAll = () => {
    setSelectedIds(new Set());
    setIsSelectionMode(false);
  };

  // Bulk actions
  const handleBulkActivate = async () => {
    const ids = Array.from(selectedIds);
    try {
      await Promise.all(ids.map((id) => setFabricStatus(id, "active")));
      await fetchFabrics();
      setSelectedIds(new Set());
      setIsSelectionMode(false);
    } catch (e) {
      console.error("Bulk activate failed:", e);
      alert("Error al activar familias");
    }
  };

  const handleBulkDeactivate = async () => {
    const ids = Array.from(selectedIds);
    try {
      await Promise.all(ids.map((id) => setFabricStatus(id, "inactive")));
      await fetchFabrics();
      setSelectedIds(new Set());
      setIsSelectionMode(false);
    } catch (e) {
      console.error("Bulk deactivate failed:", e);
      alert("Error al desactivar familias");
    }
  };

  const handleBulkDelete = async () => {
    if (!confirm(`¿Eliminar ${selectedIds.size} familias seleccionadas?`)) {
      return;
    }
    // TODO: Implement bulk delete
    alert("Función de eliminación masiva próximamente");
  };

  // Color drag-and-drop
  const handleColorMove = async (colorId: number, targetFamilyId: number) => {
    try {
      await moveColorToFamily(colorId, targetFamilyId);
      await fetchFabrics();
    } catch (e) {
      console.error("Move color failed:", e);
      alert("Error al mover el color");
    }
  };

  // Reset filters
  const handleResetFilters = () => {
    setFilters({
      status: "all",
      sortBy: "name",
      sortOrder: "asc",
    });
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
        <div className="mb-6 flex flex-col gap-4">
          {/* Top Row: Search and Actions */}
          <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
            {/* Search */}
            <SearchBar
              value={searchQuery}
              onChange={setSearchQuery}
              placeholder="Buscar familias, telas..."
            />

            {/* Actions */}
            <div className="flex gap-3">
              <LuxuryButton
                variant="secondary"
                size="md"
                onClick={() => setIsSelectionMode(!isSelectionMode)}
              >
                {isSelectionMode ? "Cancelar selección" : "Seleccionar"}
              </LuxuryButton>
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

          {/* Filter Panel */}
          <FilterPanel
            filters={filters}
            onChange={setFilters}
            onReset={handleResetFilters}
          />
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
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredItems?.map((fabric) => (
                <FabricCard
                  key={fabric.id}
                  fabric={fabric}
                  onStatusToggle={handleStatusToggle}
                  onEdit={handleEdit}
                  onDelete={handleDelete}
                  isSelectionMode={isSelectionMode}
                  isSelected={selectedIds.has(fabric.id)}
                  onSelect={handleToggleSelection}
                  onColorMove={handleColorMove}
                />
              ))}
            </div>

            {/* Bulk Action Bar */}
            <BulkActionBar
              selectedCount={selectedIds.size}
              totalCount={filteredItems?.length || 0}
              onSelectAll={handleSelectAll}
              onDeselectAll={handleDeselectAll}
              onBulkActivate={handleBulkActivate}
              onBulkDeactivate={handleBulkDeactivate}
              onBulkDelete={handleBulkDelete}
            />
          </>
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
                telas totales
              </div>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
