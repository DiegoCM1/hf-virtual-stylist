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
  isSelectionMode?: boolean;
  isSelected?: boolean;
  onSelect?: (id: number) => void;
  onColorMove?: (colorId: number, targetFamilyId: number) => void;
}

export function FabricCard({
  fabric,
  onStatusToggle,
  onEdit,
  onDelete,
  isSelectionMode = false,
  isSelected = false,
  onSelect,
  onColorMove,
}: FabricCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false);
  const [isDragOver, setIsDragOver] = useState(false);

  // Get first active fabric swatch for preview
  const previewFabric = fabric.colors.find((c) => c.status === "active") || fabric.colors[0];
  const activeFabricsCount = fabric.colors.filter((c) => c.status === "active").length;

  const handleToggleStatus = async () => {
    setIsUpdating(true);
    try {
      const newStatus = fabric.status === "active" ? "inactive" : "active";
      await onStatusToggle(fabric.id, newStatus);
    } finally {
      setIsUpdating(false);
    }
  };

  const handleCardClick = () => {
    if (isSelectionMode && onSelect) {
      onSelect(fabric.id);
    }
  };

  const handleColorDragStart = (e: React.DragEvent, colorId: number) => {
    e.stopPropagation();
    e.dataTransfer.setData("colorId", colorId.toString());
    e.dataTransfer.setData("sourceFamilyId", fabric.id.toString());
    e.dataTransfer.effectAllowed = "move";
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    const colorId = e.dataTransfer.getData("colorId");
    const sourceFamilyId = e.dataTransfer.getData("sourceFamilyId");
    if (colorId && sourceFamilyId !== fabric.id.toString()) {
      setIsDragOver(true);
      e.dataTransfer.dropEffect = "move";
    }
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);

    const colorId = e.dataTransfer.getData("colorId");
    const sourceFamilyId = e.dataTransfer.getData("sourceFamilyId");

    if (colorId && sourceFamilyId !== fabric.id.toString() && onColorMove) {
      onColorMove(parseInt(colorId), fabric.id);
    }
  };

  return (
    <div
      onClick={handleCardClick}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      className={`
        bg-white rounded-[3px] overflow-hidden
        shadow-sm
        transition-all duration-[280ms] ease-[cubic-bezier(0.2,0.7,0.2,1)]
        hover:shadow-lg
        group
        relative
        ${isSelectionMode ? "cursor-pointer" : ""}
        ${isSelected ? "ring-2 ring-gray-900 ring-offset-2" : ""}
        ${isDragOver ? "ring-2 ring-blue-500 ring-offset-2" : ""}
      `}
    >
      {/* Image Section - 4:3 Aspect Ratio */}
      <div className="relative aspect-[4/2] bg-gray-100 overflow-hidden">
        {previewFabric?.swatch_url ? (
          <>
            <Image
              src={previewFabric.swatch_url}
              alt={`${fabric.display_name} swatch preview`}
              fill
              className="object-cover"
              sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"
            />
            <div className="absolute inset-0 flex items-center justify-center">
              <span className="font-header text-white tracking-[0.2em] text-lg px-4 text-center">
                {fabric.display_name}
              </span>
            </div>
          </>
        ) : previewFabric?.hex_value ? (
          // Fallback to hex color for category indication
          <div
            className="w-full h-full"
            style={{ backgroundColor: previewFabric.hex_value }}
          />
        ) : (
          // No fabrics available
          <div className="w-full h-full flex items-center justify-center text-gray-400">
            <span className="font-body text-sm">Sin telas</span>
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

        {/* Selection Checkbox - Top Left */}
        {isSelectionMode && (
          <div className="absolute top-3 left-3 z-20">
            <div
              className={`
                w-6 h-6 rounded-full border-2 flex items-center justify-center
                transition-all duration-150
                ${
                  isSelected
                    ? "bg-gray-900 border-gray-900"
                    : "bg-white border-gray-300 hover:border-gray-400"
                }
              `}
            >
              {isSelected && (
                <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                </svg>
              )}
            </div>
          </div>
        )}

        {/* Status Badge - Top Right */}
        <div className="absolute top-3 right-3 z-10">
          <span
            className={`
              inline-flex items-center px-3 py-1 rounded-full
              font-body text-xs font-medium backdrop-blur-sm
              ${
                fabric.status === "active"
                  ? "bg-green-500/90 text-white"
                  : "bg-gray-500/90 text-white"
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
            <h3 className="font-header text-lg tracking-[0.1em] text-gray-900 truncate">
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
            <span className="font-medium text-gray-900">
              {activeFabricsCount}
            </span>{" "}
            {activeFabricsCount === 1 ? "tela activa" : "telas activas"}
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

        {/* Expand/Collapse Fabrics */}
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
          <span>{isExpanded ? "Ocultar telas" : "Ver telas"}</span>
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

        {/* Expanded Fabrics Grid */}
        {isExpanded && (
          <div className="mt-4 grid grid-cols-3 gap-3">
            {fabric.colors.map((fabricItem) => (
              <div
                key={fabricItem.id}
                draggable={onColorMove !== undefined}
                onDragStart={(e) => handleColorDragStart(e, fabricItem.id)}
                className={`relative group/fabric ${onColorMove ? "cursor-move" : ""}`}
                title={`${fabricItem.name} - ${fabricItem.status}${onColorMove ? " (Arrastrar para mover)" : ""}`}
              >
                <div className="aspect-square rounded-[3px] overflow-hidden border border-gray-200 bg-gray-50">
                  {fabricItem.swatch_url ? (
                    <Image
                      src={fabricItem.swatch_url}
                      alt={fabricItem.name}
                      width={120}
                      height={120}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                      // Fallback: show elegant hex color preview
                      <div
                        className="w-full h-full relative"
                        style={{ backgroundColor: fabricItem.hex_value }}
                      >
                        {/* Subtle texture overlay */}
                        <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent" />
                        {/* Color code badge */}
                        <div className="absolute bottom-2 left-2 right-2">
                          <div className="bg-white/90 backdrop-blur-sm rounded px-2 py-1 text-center">
                            <span className="font-body text-[10px] font-medium text-gray-700">
                              {fabricItem.hex_value}
                            </span>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                  {/* Status indicator */}
                  <div
                    className={`
                      absolute top-2 right-2 w-3 h-3 rounded-full border-2 border-white shadow-sm
                      ${fabricItem.status === "active" ? "bg-green-500" : "bg-gray-400"}
                    `}
                  />
                  {/* Fabric name tooltip */}
                  <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/90 to-transparent text-white text-[11px] px-2 py-2 opacity-0 group-hover/fabric:opacity-100 transition-opacity">
                    <div className="font-medium truncate">{fabricItem.name}</div>
                    <div className="text-[9px] text-white/70 truncate">{fabricItem.color_id}</div>
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
