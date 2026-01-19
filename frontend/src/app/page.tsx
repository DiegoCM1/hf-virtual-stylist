"use client";

import { LogoHeader } from "@/components/LogoHeader";
import { CatalogSelector } from "@/components/CatalogSelector";
import { GenerateButton } from "@/components/GenerateButton";
import SearchTela from "@/components/SearchTela";
import { ImageUploadControls } from "@/components/ImageUploadControls";
import { CustomSwatchBanner } from "@/components/CustomSwatchBanner";
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
    clearCustomSwatch,
    openImage,
    closeImage,
  } = useVirtualStylist();

  const disableGenerate = isGenerating || !familyId || !colorId;
  const errorMessage = generationError ?? catalogError;
  const showEmptyState = images.length === 0 && !isGenerating;

  return (
    <main className="h-screen w-full px-4 sm:px-6 lg:px-8 py-6 overflow-hidden flex flex-col">
      <div className="max-w-7xl mx-auto w-full">
        <LogoHeader />
      </div>

      <div className="max-w-7xl mx-auto w-full flex-1 overflow-hidden flex flex-col">
        <section className="grid gap-6 lg:grid-cols-12 flex-1 overflow-hidden">
          <div className="lg:col-span-4 space-y-4 overflow-y-auto pr-2">
          {/* Family Selector and Search in same row */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm block mb-2 font-body text-gray-700 font-medium">Familia de tela</label>
              <select
                className="border border-gray-300 rounded-[3px] px-4 py-3 w-full bg-white text-gray-900 font-body text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent transition-all"
                value={familyId}
                onChange={(event) => selectFamily(event.target.value)}
              >
                {families.map((family) => (
                  <option key={family.family_id} value={family.family_id}>
                    {family.display_name}
                  </option>
                ))}
              </select>
            </div>

            <SearchTela
              catalog={catalog}
              currentFamilyId={familyId}
              currentColorId={colorId}
              onSelect={(nextFamilyId, nextColorId) => {
                selectFamily(nextFamilyId);
                selectColor(nextColorId);
              }}
            />
          </div>

          {/* Custom swatch banner - shows above catalog when image uploaded */}
          {preview && (
            <CustomSwatchBanner preview={preview} onDiscard={clearCustomSwatch} />
          )}

          <CatalogSelector
            families={families}
            selectedFamilyId={familyId}
            selectedColorId={colorId}
            onFamilyChange={selectFamily}
            onColorSelect={selectColor}
            hasCustomSwatch={!!preview}
          />

          <GenerateButton onClick={generate} disabled={disableGenerate} loading={isGenerating} />

          {errorMessage && <div className="text-red-600 text-sm">{errorMessage}</div>}

          <ImageUploadControls
            galleryInputRef={galleryInputRef}
            cameraInputRef={cameraInputRef}
            onFileChange={handleFileSelection}
            onOpenGallery={openGalleryPicker}
            onOpenCamera={openCameraPicker}
            hasCustomSwatch={!!preview}
          />
        </div>

          <div className="lg:col-span-8 space-y-4 overflow-y-auto pl-2">
            {showEmptyState && <EmptyState />}

            {isGenerating && <LoadingState />}

            <GeneratedImageGallery images={images} onSelect={openImage} />
          </div>
        </section>
      </div>

      <ImageModal image={selectedImage} onClose={closeImage} />
    </main>
  );
}
