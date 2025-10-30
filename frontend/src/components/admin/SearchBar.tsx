"use client";

import { useState, useEffect } from "react";

interface SearchBarProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  onSearch?: (value: string) => void;
  debounceMs?: number;
}

export function SearchBar({
  value,
  onChange,
  placeholder = "Buscar...",
  onSearch,
  debounceMs = 300,
}: SearchBarProps) {
  const [localValue, setLocalValue] = useState(value);

  // Debounce search
  useEffect(() => {
    const timer = setTimeout(() => {
      onChange(localValue);
      if (onSearch) {
        onSearch(localValue);
      }
    }, debounceMs);

    return () => clearTimeout(timer);
  }, [localValue, debounceMs, onChange, onSearch]);

  // Sync with external value changes
  useEffect(() => {
    setLocalValue(value);
  }, [value]);

  const handleClear = () => {
    setLocalValue("");
    onChange("");
    if (onSearch) {
      onSearch("");
    }
  };

  return (
    <div className="relative max-w-md w-full">
      {/* Search Icon */}
      <div className="absolute left-4 top-1/2 -translate-y-1/2 pointer-events-none">
        <svg
          className="w-5 h-5 text-gray-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
          />
        </svg>
      </div>

      {/* Input */}
      <input
        type="text"
        value={localValue}
        onChange={(e) => setLocalValue(e.target.value)}
        placeholder={placeholder}
        className="
          w-full
          px-4 py-3 pl-12 pr-10
          border border-[var(--color-border)]
          rounded-[3px]
          font-body text-sm
          bg-white
          focus:outline-none
          focus:border-[var(--color-dark)]
          focus:ring-1
          focus:ring-[var(--color-dark)]
          transition-colors duration-150
          placeholder:text-gray-400
        "
      />

      {/* Clear Button */}
      {localValue && (
        <button
          type="button"
          onClick={handleClear}
          className="
            absolute right-3 top-1/2 -translate-y-1/2
            p-1 rounded-full
            text-gray-400 hover:text-gray-600
            hover:bg-gray-100
            transition-colors duration-150
          "
          aria-label="Clear search"
        >
          <svg
            className="w-4 h-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>
      )}
    </div>
  );
}
