"use client";

import Image from "next/image";
import { useState } from "react";
import type { FabricRead } from "@/types/admin";
import { StatusToggle } from "./StatusToggle";
import { LuxuryButton } from "./LuxuryButton";

interface FabricCardProps {
  fabric: FabricRead;
  onStatusToggle: (id: number, status: "active" | "inactive") => Promise<void>;
  onEdit?: (fabric: FabricRead) => void;
  onDelete?: (id: number) => void;
}

export function FabricCard({
  fabric,
  onStatusToggle,
  onEdit,
  onDelete,
}: FabricCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false);

  // Get first active color's swatch for preview
  const previewColor = fabric.colors.find((c) => c.status === "active") || fabric.colors[0];
  const activeColorsCount = fabric.colors.filter((c) => c.status === "active").length;

  const handleToggleStatus = async () => {
    setIsUpdating(true);
    try {
      const newStatus = fabric.status === "active" ? "inactive" : "active";
      await onStatusToggle(fabric.id, newStatus);
    } finally {
      setIsUpdating(false);
    }
  };

  return (
    <div
      className="
        bg-white rounded-[3px] overflow-hidden
        shadow-[var(--shadow-sm)]
        transition-all duration-[280ms] ease-[cubic-bezier(0.2,0.7,0.2,1)]
        hover:shadow-[var(--shadow-elevated)]
        group
      "
    >
      {/* Image Section - 4:3 Aspect Ratio */}
      <div className="relative aspect-[4/3] bg-gray-100 overflow-hidden">
        {previewColor?.swatch_url ? (
          <Image
            src={previewColor.swatch_url}
            alt={`${fabric.display_name} swatch preview`}
            fill
            className="object-cover"
            sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"
          />
        ) : previewColor?.hex_value ? (
          // Fallback to hex color
          <div
            className="w-full h-full"
            style={{ backgroundColor: previewColor.hex_value }}
          />
        ) : (
          // No colors available
          <div className="w-full h-full flex items-center justify-center text-gray-400">
            <span className="font-body text-sm">Sin muestras</span>
          </div>
        )}

        {/* Overlay on hover */}
        <div
          className="
            absolute inset-0
            bg-black/60
            opacity-0 group-hover:opacity-100
            transition-opacity duration-[280ms]
            flex items-center justify-center
          "
        >
          <span className="font-header text-white tracking-[0.2em] text-lg px-4 text-center">
            {fabric.display_name}
          </span>
        </div>

        {/* Status Badge - Top Right */}
        <div className="absolute top-3 right-3">
          <span
            className={`
              inline-flex items-center px-3 py-1 rounded-full
              font-body text-xs font-medium backdrop-blur-sm
              ${
                fabric.status === "active"
                  ? "bg-[var(--color-active)]/90 text-white"
                  : "bg-[var(--color-inactive)]/90 text-white"
              }
            `}
          >
            {fabric.status === "active" ? "Activo" : "Inactivo"}
          </span>
        </div>
      </div>

      {/* Content Section */}
      <div className="p-6">
        {/* Header */}
        <div className="flex items-start justify-between mb-3">
          <div className="flex-1 min-w-0">
            <h3 className="font-header text-lg tracking-[0.1em] text-[var(--color-dark)] truncate">
              {fabric.display_name}
            </h3>
            <p className="font-body text-sm text-gray-600 mt-1">
              {fabric.family_id}
            </p>
          </div>
        </div>

        {/* Stats */}
        <div className="flex items-center gap-4 mb-4 text-sm">
          <div className="font-body text-gray-600">
            <span className="font-medium text-[var(--color-dark)]">
              {activeColorsCount}
            </span>{" "}
            {activeColorsCount === 1 ? "color activo" : "colores activos"}
          </div>
          <div className="font-body text-gray-400">
            {fabric.colors.length} total
          </div>
        </div>

        {/* Status Toggle */}
        <div className="flex items-center justify-between mb-4 pb-4 border-b border-gray-200">
          <span className="font-body text-sm text-gray-600">Estado:</span>
          <StatusToggle
            status={fabric.status}
            onChange={handleToggleStatus}
            disabled={isUpdating}
            label
          />
        </div>

        {/* Expand/Collapse Colors */}
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="
            w-full py-2 px-4 rounded-[3px]
            border border-gray-200
            font-body text-sm text-gray-700
            hover:bg-gray-50 hover:border-gray-300
            transition-colors duration-150
            flex items-center justify-between
          "
        >
          <span>{isExpanded ? "Ocultar colores" : "Ver colores"}</span>
          <svg
            className={`w-4 h-4 transition-transform ${isExpanded ? "rotate-180" : ""}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M19 9l-7 7-7-7"
            />
          </svg>
        </button>

        {/* Expanded Colors Grid */}
        {isExpanded && (
          <div className="mt-4 grid grid-cols-4 gap-2">
            {fabric.colors.map((color) => (
              <div
                key={color.id}
                className="relative group/color"
                title={`${color.name} - ${color.status}`}
              >
                <div className="aspect-square rounded-[3px] overflow-hidden border border-gray-200">
                  {color.swatch_url ? (
                    <Image
                      src={color.swatch_url}
                      alt={color.name}
                      width={80}
                      height={80}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div
                      className="w-full h-full"
                      style={{ backgroundColor: color.hex_value }}
                    />
                  )}
                </div>
                {/* Status indicator */}
                <div
                  className={`
                    absolute top-1 right-1 w-2 h-2 rounded-full
                    ${color.status === "active" ? "bg-green-500" : "bg-gray-400"}
                  `}
                />
                {/* Color name tooltip */}
                <div className="absolute inset-x-0 bottom-0 bg-black/75 text-white text-[10px] p-1 text-center opacity-0 group-hover/color:opacity-100 transition-opacity truncate">
                  {color.name}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Actions */}
        {(onEdit || onDelete) && (
          <div className="flex gap-2 mt-4">
            {onEdit && (
              <LuxuryButton
                variant="secondary"
                size="sm"
                fullWidth
                onClick={() => onEdit(fabric)}
              >
                Editar
              </LuxuryButton>
            )}
            {onDelete && (
              <LuxuryButton
                variant="danger"
                size="sm"
                onClick={() => {
                  if (confirm(`¿Eliminar la familia "${fabric.display_name}"?`)) {
                    onDelete(fabric.id);
                  }
                }}
              >
                Eliminar
              </LuxuryButton>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
