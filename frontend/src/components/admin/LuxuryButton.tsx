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

  // Variant classes
  const variantClasses = {
    primary: "bg-gray-900 text-white border-transparent hover:brightness-110",
    secondary: "bg-white text-gray-900 border-gray-900 hover:bg-gray-50",
    danger: "bg-red-500 text-white border-transparent hover:brightness-110",
    ghost: "bg-transparent text-gray-900 border-transparent hover:bg-gray-50",
  };

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`
        font-body font-medium
        rounded-[3px]
        border
        transition-all duration-[280ms] ease-[cubic-bezier(0.2,0.7,0.2,1)]
        ${sizeClasses[size]}
        ${variantClasses[variant]}
        ${fullWidth ? "w-full" : ""}
        ${disabled ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}
        ${variant !== "ghost" ? "hover:-translate-y-[3px] hover:shadow-lg" : ""}
        active:translate-y-0
        flex items-center justify-center gap-2
      `}
    >
      {icon && <span className="flex-shrink-0">{icon}</span>}
      <span>{children}</span>
    </button>
  );
}
