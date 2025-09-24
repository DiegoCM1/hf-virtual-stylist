import Image from "next/image";
import { GeneratedImage } from "@/types/catalog";

type GeneratedImageGalleryProps = {
  images: GeneratedImage[];
  onSelect: (image: GeneratedImage) => void;
};

export function GeneratedImageGallery({ images, onSelect }: GeneratedImageGalleryProps) {
  if (images.length === 0) {
    return null;
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {images.map((image) => (
        <figure key={image.cut} className="border rounded p-2">
          <Image
            src={image.url}
            alt={image.cut}
            width={image.width || 800}
            height={image.height || 1200}
            className="w-full h-auto rounded cursor-zoom-in"
            sizes="(min-width: 768px) 50vw, 100vw"
            onClick={() => onSelect(image)}
          />
          <figcaption className="text-sm mt-1 capitalize">{image.cut}</figcaption>
        </figure>
      ))}
    </div>
  );
}
