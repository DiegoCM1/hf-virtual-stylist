"use client";

import { useEffect, useState } from "react";

const STAGES = [
  {
    key: "init",
    label: "Inicializando modelo SDXL",
    duration: 2000,
  },
  {
    key: "control",
    label: "Aplicando guías ControlNet",
    duration: 3000,
  },
  {
    key: "texture",
    label: "Renderizando textura de tela",
    duration: 4000,
  },
  {
    key: "refine",
    label: "Refinando detalles",
    duration: 3000,
  },
  {
    key: "finalize",
    label: "Finalizando renders…",
    duration: 2000,
  },
];

export function LoadingState() {
  const [currentStage, setCurrentStage] = useState(0);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    // Animate progress bar
    const progressInterval = setInterval(() => {
      setProgress((prev) => {
        const increment = Math.random() * 2 + 0.5; // Random increment for organic feel
        return Math.min(prev + increment, 95); // Cap at 95% until complete
      });
    }, 100);

    // Stage progression
    const stageInterval = setInterval(() => {
      setCurrentStage((prev) => {
        if (prev < STAGES.length - 1) {
          return prev + 1;
        }
        return prev;
      });
    }, 3000);

    return () => {
      clearInterval(progressInterval);
      clearInterval(stageInterval);
    };
  }, []);

  return (
    <div className="flex items-center justify-center min-h-[400px]">
      <div className="w-full max-w-xl space-y-8 px-6">
        {/* Logo Spinner */}
        <div className="flex justify-center">
          <div className="relative">
            {/* Outer ring */}
            <div className="w-20 h-20 rounded-full border-2 border-gray-200 animate-spin-slow">
              <div className="absolute top-0 left-1/2 w-2 h-2 -mt-1 -ml-1 bg-gray-900 rounded-full"></div>
            </div>
            {/* Inner subtle glow */}
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-12 h-12 bg-gray-900/5 rounded-full animate-pulse-slow"></div>
            </div>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="space-y-3">
          <div className="h-1 bg-gray-100 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-gray-800 via-gray-900 to-black transition-all duration-300 ease-out"
              style={{ width: `${progress}%` }}
            >
              <div className="h-full w-full bg-gradient-to-r from-transparent via-white/20 to-transparent animate-shimmer"></div>
            </div>
          </div>

          <div className="flex justify-between items-center text-xs text-gray-500">
            <span>{Math.round(progress)}%</span>
            <span className="font-light">Generando renders de alta calidad</span>
          </div>
        </div>

        {/* Current Stage */}
        <div className="space-y-4">
          <div className="text-center">
            <p className="text-sm font-light text-gray-900 tracking-wide">
              {STAGES[currentStage].label}
            </p>
          </div>

          {/* Stage Indicators */}
          <div className="flex justify-center gap-2">
            {STAGES.map((stage, index) => (
              <div
                key={stage.key}
                className={`h-1.5 rounded-full transition-all duration-500 ${
                  index === currentStage
                    ? "w-8 bg-gray-900"
                    : index < currentStage
                    ? "w-1.5 bg-gray-400"
                    : "w-1.5 bg-gray-200"
                }`}
              />
            ))}
          </div>
        </div>

        {/* Elegant Details */}
        <div className="text-center space-y-2">
          <p className="text-xs text-gray-400 font-light tracking-wider uppercase">
            Harris & Frank Virtual Stylist
          </p>
          <p className="text-xs text-gray-400 font-light italic">
            Creando visualizaciones fotorrealistas
          </p>
        </div>

        {/* Pulsing dots for activity indication */}
        <div className="flex justify-center gap-1.5">
          <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce-delay-0"></div>
          <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce-delay-1"></div>
          <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce-delay-2"></div>
        </div>
      </div>
    </div>
  );
}
