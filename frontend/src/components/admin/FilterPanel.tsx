"use client";

import { useState } from "react";

export interface FilterOptions {
  status: "all" | "active" | "inactive";
  sortBy: "name" | "created" | "colors" | "recent";
  sortOrder: "asc" | "desc";
}

interface FilterPanelProps {
  filters: FilterOptions;
  onChange: (filters: FilterOptions) => void;
  onReset: () => void;
}

export function FilterPanel({ filters, onChange, onReset }: FilterPanelProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const hasActiveFilters =
    filters.status !== "all" ||
    filters.sortBy !== "name" ||
    filters.sortOrder !== "asc";

  return (
    <div className="bg-white rounded-[3px] border border-gray-200 overflow-hidden">
      {/* Header */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="
          w-full px-4 py-3 flex items-center justify-between
          hover:bg-gray-50 transition-colors
        "
      >
        <div className="flex items-center gap-2">
          <svg
            className="w-5 h-5 text-gray-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"
            />
          </svg>
          <span className="font-body text-sm font-medium text-gray-900">
            Filtros {hasActiveFilters && `(${getActiveFilterCount(filters)})`}
          </span>
        </div>
        <svg
          className={`w-4 h-4 text-gray-600 transition-transform ${
            isExpanded ? "rotate-180" : ""
          }`}
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

      {/* Filter Options */}
      {isExpanded && (
        <div className="px-4 pb-4 pt-2 space-y-4 border-t border-gray-200">
          {/* Status Filter */}
          <div>
            <label className="block font-body text-xs font-medium text-gray-700 mb-2 uppercase tracking-wider">
              Estado
            </label>
            <div className="grid grid-cols-3 gap-2">
              {(["all", "active", "inactive"] as const).map((status) => (
                <button
                  key={status}
                  onClick={() => onChange({ ...filters, status })}
                  className={`
                    px-3 py-2 rounded-[3px] font-body text-sm
                    transition-all duration-150
                    ${
                      filters.status === status
                        ? "bg-gray-900 text-white"
                        : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                    }
                  `}
                >
                  {status === "all" ? "Todos" : status === "active" ? "Activos" : "Inactivos"}
                </button>
              ))}
            </div>
          </div>

          {/* Sort By */}
          <div>
            <label className="block font-body text-xs font-medium text-gray-700 mb-2 uppercase tracking-wider">
              Ordenar por
            </label>
            <select
              value={filters.sortBy}
              onChange={(e) =>
                onChange({ ...filters, sortBy: e.target.value as FilterOptions["sortBy"] })
              }
              className="
                w-full px-3 py-2 rounded-[3px] border border-gray-300
                font-body text-sm text-gray-900
                focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent
              "
            >
              <option value="name">Nombre (A-Z)</option>
              <option value="created">Fecha de creación</option>
              <option value="colors">Número de telas</option>
              <option value="recent">Actualizado recientemente</option>
            </select>
          </div>

          {/* Sort Order */}
          <div>
            <label className="block font-body text-xs font-medium text-gray-700 mb-2 uppercase tracking-wider">
              Orden
            </label>
            <div className="grid grid-cols-2 gap-2">
              {(["asc", "desc"] as const).map((order) => (
                <button
                  key={order}
                  onClick={() => onChange({ ...filters, sortOrder: order })}
                  className={`
                    px-3 py-2 rounded-[3px] font-body text-sm
                    transition-all duration-150
                    flex items-center justify-center gap-2
                    ${
                      filters.sortOrder === order
                        ? "bg-gray-900 text-white"
                        : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                    }
                  `}
                >
                  {order === "asc" ? (
                    <>
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M3 4h13M3 8h9m-9 4h6m4 0l4-4m0 0l4 4m-4-4v12"
                        />
                      </svg>
                      Ascendente
                    </>
                  ) : (
                    <>
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M3 4h13M3 8h9m-9 4h9m5-4v12m0 0l-4-4m4 4l4-4"
                        />
                      </svg>
                      Descendente
                    </>
                  )}
                </button>
              ))}
            </div>
          </div>

          {/* Reset Filters */}
          {hasActiveFilters && (
            <button
              onClick={onReset}
              className="
                w-full py-2 px-4 rounded-[3px]
                border border-gray-300 bg-white
                font-body text-sm text-gray-700
                hover:bg-gray-50 transition-colors
              "
            >
              Restablecer filtros
            </button>
          )}
        </div>
      )}
    </div>
  );
}

function getActiveFilterCount(filters: FilterOptions): number {
  let count = 0;
  if (filters.status !== "all") count++;
  if (filters.sortBy !== "name") count++;
  if (filters.sortOrder !== "asc") count++;
  return count;
}
