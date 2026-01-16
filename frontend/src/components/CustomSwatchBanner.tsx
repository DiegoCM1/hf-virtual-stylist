import Image from "next/image";
import { PreviewImage } from "@/types/catalog";

type CustomSwatchBannerProps = {
  preview: PreviewImage;
  onDiscard: () => void;
};

export function CustomSwatchBanner({ preview, onDiscard }: CustomSwatchBannerProps) {
  return (
    <div className="rounded-[3px] border border-gray-300 bg-white shadow-sm p-3">
      <div className="flex items-center gap-3">
        {/* Thumbnail */}
        <div className="relative w-16 h-16 flex-shrink-0 rounded-[3px] overflow-hidden border border-gray-200">
          <Image
            src={preview.url}
            alt={`Vista previa de ${preview.name}`}
            fill
            className="object-cover"
            unoptimized
          />
        </div>

        {/* Info */}
        <div className="flex-1 min-w-0">
          <div className="text-sm font-body font-medium text-gray-900">
            Imagen personalizada
          </div>
          <div className="text-xs font-body text-gray-500 truncate">
            {preview.name}
          </div>
        </div>

        {/* Discard button */}
        <button
          type="button"
          onClick={onDiscard}
          className="
            flex-shrink-0
            w-8 h-8 rounded-full
            bg-gray-100 hover:bg-gray-200
            text-gray-600 hover:text-gray-900
            flex items-center justify-center
            transition-colors duration-200
            focus:outline-none focus:ring-2 focus:ring-gray-900 focus:ring-offset-2
          "
          aria-label="Descartar imagen personalizada"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
          </svg>
        </button>
      </div>
    </div>
  );
}
