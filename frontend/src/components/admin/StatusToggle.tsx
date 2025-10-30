"use client";

interface StatusToggleProps {
  status: "active" | "inactive";
  onChange: (status: "active" | "inactive") => void;
  disabled?: boolean;
  label?: boolean;
  size?: "sm" | "md";
}

export function StatusToggle({
  status,
  onChange,
  disabled = false,
  label = false,
  size = "md",
}: StatusToggleProps) {
  const isActive = status === "active";

  // Size configurations
  const sizes = {
    sm: {
      container: "w-10 h-5",
      circle: "w-3 h-3 top-1 left-1",
      activeTransform: "translateX(0px)",
      inactiveTransform: "translateX(16px)",
    },
    md: {
      container: "w-12 h-6",
      circle: "w-4 h-4 top-1 left-1",
      activeTransform: "translateX(0px)",
      inactiveTransform: "translateX(20px)",
    },
  };

  const config = sizes[size];

  return (
    <div className="flex items-center gap-2">
      <button
        type="button"
        role="switch"
        aria-checked={isActive}
        aria-label={`Toggle status: ${status}`}
        onClick={() => onChange(isActive ? "inactive" : "active")}
        disabled={disabled}
        className={`
          relative rounded-full transition-colors duration-150
          ${config.container}
          ${isActive ? "bg-green-500" : "bg-gray-500"}
          ${disabled ? "opacity-50 cursor-not-allowed" : "cursor-pointer hover:brightness-110"}
        `}
      >
        <span
          className={`
            absolute bg-white rounded-full transition-transform duration-150
            ${config.circle}
          `}
          style={{
            transform: isActive ? config.activeTransform : config.inactiveTransform,
          }}
        />
      </button>

      {label && (
        <span
          className={`font-body text-xs font-medium ${
            isActive ? "text-green-500" : "text-gray-500"
          }`}
        >
          {isActive ? "Activo" : "Inactivo"}
        </span>
      )}
    </div>
  );
}
