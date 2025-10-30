"use client";

import { ReactNode } from "react";

interface LuxuryButtonProps {
  children: ReactNode;
  onClick?: () => void;
  variant?: "primary" | "secondary" | "danger" | "ghost";
  size?: "sm" | "md" | "lg";
  disabled?: boolean;
  fullWidth?: boolean;
  type?: "button" | "submit" | "reset";
  icon?: ReactNode;
}

export function LuxuryButton({
  children,
  onClick,
  variant = "primary",
  size = "md",
  disabled = false,
  fullWidth = false,
  type = "button",
  icon,
}: LuxuryButtonProps) {
  // Size classes
  const sizeClasses = {
    sm: "px-4 py-2 text-xs",
    md: "px-6 py-3 text-sm",
    lg: "px-8 py-4 text-base",
  };

  // Variant styles
  const variantStyles = {
    primary: {
      bg: "var(--color-dark)",
      text: "var(--color-white)",
      border: "transparent",
      hover: "hover:brightness-110",
    },
    secondary: {
      bg: "var(--color-white)",
      text: "var(--color-dark)",
      border: "var(--color-dark)",
      hover: "hover:bg-[var(--color-bg-light)]",
    },
    danger: {
      bg: "var(--color-danger)",
      text: "var(--color-white)",
      border: "transparent",
      hover: "hover:brightness-110",
    },
    ghost: {
      bg: "transparent",
      text: "var(--color-dark)",
      border: "transparent",
      hover: "hover:bg-[var(--color-bg-light)]",
    },
  };

  const variantStyle = variantStyles[variant];

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`
        font-body font-medium
        rounded-[3px]
        transition-all duration-[280ms] ease-[cubic-bezier(0.2,0.7,0.2,1)]
        ${sizeClasses[size]}
        ${fullWidth ? "w-full" : ""}
        ${disabled ? "opacity-50 cursor-not-allowed" : `cursor-pointer ${variantStyle.hover}`}
        ${variant !== "ghost" ? "hover:-translate-y-[3px] hover:shadow-[var(--shadow-elevated)]" : ""}
        active:translate-y-0
        flex items-center justify-center gap-2
      `}
      style={{
        backgroundColor: variantStyle.bg,
        color: variantStyle.text,
        border: `1px solid ${variantStyle.border}`,
      }}
    >
      {icon && <span className="flex-shrink-0">{icon}</span>}
      <span>{children}</span>
    </button>
  );
}
