import Image from "next/image";
import { GeneratedImage } from "@/types/catalog";

type ImageModalProps = {
  image: GeneratedImage | null;
  onClose: () => void;
};

export function ImageModal({ image, onClose }: ImageModalProps) {
  if (!image) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center" aria-modal="true" role="dialog">
      <div className="absolute inset-0 bg-black/70" onClick={onClose} />
      <div className="relative max-w-5xl w-[92vw] md:w-auto p-0" onClick={(event) => event.stopPropagation()}>
        <button
          aria-label="Cerrar"
          className="absolute -top-10 right-0 md:top-2 md:-right-10 bg-white/10 hover:bg-white/20 text-white rounded-full px-3 py-1 text-sm"
          onClick={onClose}
          type="button"
        >
          ✕
        </button>
        <Image
          src={image.url}
          alt={image.cut}
          width={image.width || 1200}
          height={image.height || 1600}
          className="rounded shadow-lg max-h-[85vh] w-auto h-auto"
          sizes="85vh"
          priority
        />
        <div className="mt-2 text-center text-sm text-white/80 capitalize">
          {image.cut} · Toca fuera para cerrar
        </div>
      </div>
    </div>
  );
}
