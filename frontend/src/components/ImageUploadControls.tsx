import { RefObject } from "react";
import Image from "next/image";
import { PreviewImage } from "@/types/catalog";

type ImageUploadControlsProps = {
  galleryInputRef: RefObject<HTMLInputElement>;
  cameraInputRef: RefObject<HTMLInputElement>;
  onFileChange: (files: FileList | null) => void;
  onOpenGallery: () => void;
  onOpenCamera: () => void;
  preview: PreviewImage | null;
};

export function ImageUploadControls({
  galleryInputRef,
  cameraInputRef,
  onFileChange,
  onOpenGallery,
  onOpenCamera,
  preview,
}: ImageUploadControlsProps) {
  return (
    <div className="space-y-2">
      <input
        ref={galleryInputRef}
        type="file"
        accept="image/*"
        className="hidden"
        onChange={(event) => {
          onFileChange(event.target.files);
          event.target.value = "";
        }}
      />
      <input
        ref={cameraInputRef}
        type="file"
        accept="image/*"
        capture="environment"
        className="hidden"
        onChange={(event) => {
          onFileChange(event.target.files);
          event.target.value = "";
        }}
      />
      <div className="flex flex-col gap-2 sm:flex-row">
        <button
          type="button"
          className="w-full rounded border border-white/20 bg-white/10 px-3 py-2 text-sm text-white hover:bg-white/20"
          onClick={onOpenGallery}
        >
          Elegir foto
        </button>
        <button
          type="button"
          className="w-full rounded border border-white/20 bg-white/10 px-3 py-2 text-sm text-white hover:bg-white/20 md:hidden"
          onClick={onOpenCamera}
        >
          Tomar foto
        </button>
      </div>
      {preview && (
        <div className="space-y-2">
          <div className="text-sm text-white/70">Vista previa</div>
          <div className="overflow-hidden rounded border border-white/10 bg-black/20">
            <Image
              src={preview.url}
              alt={`Vista previa de ${preview.name}`}
              width={preview.width || 400}
              height={preview.height || 400}
              className="h-auto w-full object-cover"
              unoptimized
            />
          </div>
        </div>
      )}
    </div>
  );
}
