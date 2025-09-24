"use client";

import { LogoHeader } from "@/components/LogoHeader";
import { CatalogSelector } from "@/components/CatalogSelector";
import { GenerateButton } from "@/components/GenerateButton";
import SearchTela from "@/components/SearchTela";
import { ImageUploadControls } from "@/components/ImageUploadControls";
import { GeneratedImageGallery } from "@/components/GeneratedImageGallery";
import { ImageModal } from "@/components/ImageModal";
import { LoadingState } from "@/components/LoadingState";
import { EmptyState } from "@/components/EmptyState";
import { useVirtualStylist } from "@/hooks/useVirtualStylist";

export default function Home() {
  const {
    catalog,
    families,
    catalogError,
    familyId,
    colorId,
    isGenerating,
    generationError,
    images,
    selectedImage,
    preview,
    galleryInputRef,
    cameraInputRef,
    selectFamily,
    selectColor,
    generate,
    handleFileSelection,
    openGalleryPicker,
    openCameraPicker,
    openImage,
    closeImage,
  } = useVirtualStylist();

  const disableGenerate = isGenerating || !familyId || !colorId;
  const errorMessage = generationError ?? catalogError;
  const showEmptyState = images.length === 0 && !isGenerating;

  return (
    <main className="min-h-screen max-w-4xl mx-auto p-6">
      <LogoHeader />

      <section className="grid gap-4 md:grid-cols-3">
        <div className="md:col-span-1 space-y-4">
          <CatalogSelector
            families={families}
            selectedFamilyId={familyId}
            selectedColorId={colorId}
            onFamilyChange={selectFamily}
            onColorSelect={selectColor}
          />

          <GenerateButton onClick={generate} disabled={disableGenerate} loading={isGenerating} />

          {errorMessage && <div className="text-red-600 text-sm">{errorMessage}</div>}

          <div className="w-full flex text-white py-2 justify-center">O</div>

          <SearchTela
            catalog={catalog}
            currentFamilyId={familyId}
            currentColorId={colorId}
            onSelect={(nextFamilyId, nextColorId) => {
              selectFamily(nextFamilyId);
              selectColor(nextColorId);
            }}
          />

          <ImageUploadControls
            galleryInputRef={galleryInputRef}
            cameraInputRef={cameraInputRef}
            onFileChange={handleFileSelection}
            onOpenGallery={openGalleryPicker}
            onOpenCamera={openCameraPicker}
            preview={preview}
          />
        </div>

        <div className="md:col-span-2 space-y-4">
          {showEmptyState && <EmptyState />}

          {isGenerating && <LoadingState />}

          <GeneratedImageGallery images={images} onSelect={openImage} />
        </div>
      </section>

      <ImageModal image={selectedImage} onClose={closeImage} />
    </main>
  );
}
