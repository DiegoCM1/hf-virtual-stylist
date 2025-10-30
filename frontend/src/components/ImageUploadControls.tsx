import { RefObject } from "react";
import Image from "next/image";
import { PreviewImage } from "@/types/catalog";

type ImageUploadControlsProps = {
  galleryInputRef: RefObject<HTMLInputElement | null>;
  cameraInputRef: RefObject<HTMLInputElement | null>;
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
      <div className="flex flex-col gap-3 sm:flex-row">
        <button
          type="button"
          className="
            flex-1 bg-white border border-gray-300
            px-6 py-3 rounded-[3px]
            font-body text-sm font-medium text-gray-900
            shadow-sm
            transition-all duration-200
            hover:bg-gray-50 hover:border-gray-900 hover:shadow-md hover:-translate-y-0.5
            active:translate-y-0
            focus:outline-none focus:ring-2 focus:ring-gray-900 focus:ring-offset-2
          "
          onClick={onOpenGallery}
        >
          📁 Elegir Foto
        </button>
        <button
          type="button"
          className="
            flex-1 bg-white border border-gray-300
            px-6 py-3 rounded-[3px]
            font-body text-sm font-medium text-gray-900
            shadow-sm
            transition-all duration-200
            hover:bg-gray-50 hover:border-gray-900 hover:shadow-md hover:-translate-y-0.5
            active:translate-y-0
            focus:outline-none focus:ring-2 focus:ring-gray-900 focus:ring-offset-2
            md:hidden
          "
          onClick={onOpenCamera}
        >
          📷 Tomar Foto
        </button>
      </div>
      {preview && (
        <div className="space-y-2 mt-4">
          <div className="text-sm font-body text-gray-700 font-medium">Vista previa</div>
          <div className="overflow-hidden rounded-[3px] border border-gray-300 bg-white shadow-sm">
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
