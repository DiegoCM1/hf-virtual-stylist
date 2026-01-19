import { RefObject } from "react";

type ImageUploadControlsProps = {
  galleryInputRef: RefObject<HTMLInputElement | null>;
  cameraInputRef: RefObject<HTMLInputElement | null>;
  onFileChange: (files: FileList | null) => void;
  onOpenGallery: () => void;
  onOpenCamera: () => void;
  hasCustomSwatch?: boolean;
};

export function ImageUploadControls({
  galleryInputRef,
  cameraInputRef,
  onFileChange,
  onOpenGallery,
  onOpenCamera,
  hasCustomSwatch = false,
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
          {hasCustomSwatch ? "📁 Cambiar Foto" : "📁 Elegir Foto"}
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
    </div>
  );
}
