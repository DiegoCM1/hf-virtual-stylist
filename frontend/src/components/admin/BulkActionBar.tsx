"use client";

import { LuxuryButton } from "./LuxuryButton";

interface BulkActionBarProps {
  selectedCount: number;
  totalCount: number;
  onSelectAll: () => void;
  onDeselectAll: () => void;
  onBulkActivate: () => void;
  onBulkDeactivate: () => void;
  onBulkDelete: () => void;
}

export function BulkActionBar({
  selectedCount,
  totalCount,
  onSelectAll,
  onDeselectAll,
  onBulkActivate,
  onBulkDeactivate,
  onBulkDelete,
}: BulkActionBarProps) {
  if (selectedCount === 0) return null;

  const allSelected = selectedCount === totalCount;

  return (
    <div
      className="
        fixed bottom-6 left-1/2 -translate-x-1/2
        bg-white rounded-[3px] shadow-2xl
        border border-gray-200
        px-6 py-4
        flex items-center gap-4
        z-50
        animate-slide-up
      "
    >
      {/* Selection Info */}
      <div className="flex items-center gap-3 pr-4 border-r border-gray-200">
        <div className="flex items-center justify-center w-8 h-8 rounded-full bg-gray-900 text-white font-body text-sm font-medium">
          {selectedCount}
        </div>
        <span className="font-body text-sm text-gray-700">
          {selectedCount === 1 ? "familia seleccionada" : "familias seleccionadas"}
        </span>
      </div>

      {/* Select All/None */}
      <button
        onClick={allSelected ? onDeselectAll : onSelectAll}
        className="font-body text-sm text-gray-900 hover:text-gray-600 transition-colors"
      >
        {allSelected ? "Deseleccionar todo" : "Seleccionar todo"}
      </button>

      {/* Bulk Actions */}
      <div className="flex items-center gap-2 pl-4 border-l border-gray-200">
        <LuxuryButton
          variant="secondary"
          size="sm"
          onClick={onBulkActivate}
        >
          Activar
        </LuxuryButton>
        <LuxuryButton
          variant="secondary"
          size="sm"
          onClick={onBulkDeactivate}
        >
          Desactivar
        </LuxuryButton>
        <LuxuryButton
          variant="danger"
          size="sm"
          onClick={onBulkDelete}
        >
          Eliminar
        </LuxuryButton>
      </div>

      {/* Close */}
      <button
        onClick={onDeselectAll}
        className="ml-2 text-gray-400 hover:text-gray-600 transition-colors"
        title="Cancelar"
      >
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
  );
}
