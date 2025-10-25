import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { getCatalog as fetchCatalog, generateImages } from "@/lib/apiClient";
import {
  CatalogResponse,
  Family,
  GeneratedImage,
  PreviewImage,
} from "@/types/catalog";

const EMPTY_CATALOG: CatalogResponse = { families: [] };

function getDefaultFamily(families: Family[]): Family | undefined {
  return families.find((family) => family.status === "active") ?? families[0];
}

export function useVirtualStylist() {
  const [catalog, setCatalog] = useState<CatalogResponse>(EMPTY_CATALOG);
  const [familyId, setFamilyId] = useState<string>("");
  const [colorId, setColorId] = useState<string>("");
  const [catalogLoading, setCatalogLoading] = useState<boolean>(true);
  const [catalogError, setCatalogError] = useState<string | null>(null);
  const [isGenerating, setIsGenerating] = useState<boolean>(false);
  const [generationError, setGenerationError] = useState<string | null>(null);
  const [images, setImages] = useState<GeneratedImage[]>([]);
  const [selectedImage, setSelectedImage] = useState<GeneratedImage | null>(null);
  const [preview, setPreview] = useState<PreviewImage | null>(null);
  const previewUrlRef = useRef<string | null>(null);
  const galleryInputRef = useRef<HTMLInputElement | null>(null);
  const cameraInputRef = useRef<HTMLInputElement | null>(null);

  useEffect(() => {
    let mounted = true;
    setCatalogLoading(true);
    fetchCatalog()
      .then((data) => {
        if (!mounted) return;
        setCatalog(data);
        const defaultFamily = getDefaultFamily(data.families);
        if (defaultFamily) {
          setFamilyId(defaultFamily.family_id);
          const firstColor = defaultFamily.colors[0];
          setColorId(firstColor ? firstColor.color_id : "");
        }
        setCatalogError(null);
      })
      .catch(() => {
        if (!mounted) return;
        setCatalogError("No se pudo cargar el catálogo");
      })
      .finally(() => {
        if (!mounted) return;
        setCatalogLoading(false);
      });

    return () => {
      mounted = false;
    };
  }, []);

  useEffect(() => {
    return () => {
      if (previewUrlRef.current) {
        URL.revokeObjectURL(previewUrlRef.current);
      }
    };
  }, []);

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setSelectedImage(null);
      }
    };

    if (selectedImage) {
      document.addEventListener("keydown", onKeyDown);
      document.body.style.overflow = "hidden";
    }

    return () => {
      document.removeEventListener("keydown", onKeyDown);
      document.body.style.overflow = "";
    };
  }, [selectedImage]);

  const currentFamily = useMemo(
    () => catalog.families.find((family) => family.family_id === familyId) ?? null,
    [catalog, familyId],
  );

  const handleFamilyChange = useCallback(
    (nextFamilyId: string) => {
      setFamilyId(nextFamilyId);
      const nextFamily = catalog.families.find(
        (family) => family.family_id === nextFamilyId,
      );

      if (!nextFamily) {
        setColorId("");
        return;
      }

      setColorId((current) => {
        const hasCurrent = nextFamily.colors.some(
          (color) => color.color_id === current,
        );
        if (hasCurrent) {
          return current;
        }
        const firstColor = nextFamily.colors[0];
        return firstColor ? firstColor.color_id : "";
      });
    },
    [catalog.families],
  );

  const handleColorSelect = useCallback((nextColorId: string) => {
    setColorId(nextColorId);
  }, []);

  const handleGenerate = useCallback(async () => {
    if (!familyId || !colorId) {
      return;
    }

    setIsGenerating(true);
    setGenerationError(null);
    setImages([]);

    try {
      const { images: generatedImages } = await generateImages({
        familyId,
        colorId,
      });
      setImages(generatedImages ?? []);
    } catch (error) {
      console.error(error);
      setGenerationError(
        "No pudimos generar las imágenes. Probemos otra combinación.",
      );
    } finally {
      setIsGenerating(false);
    }
  }, [familyId, colorId]);

  const handleFileSelection = useCallback((files: FileList | null) => {
    const file = files?.[0];
    if (!file) {
      return;
    }

    if (previewUrlRef.current) {
      URL.revokeObjectURL(previewUrlRef.current);
    }

    const objectUrl = URL.createObjectURL(file);
    previewUrlRef.current = objectUrl;

    const image = new window.Image();
    image.onload = () => {
      setPreview({
        url: objectUrl,
        name: file.name,
        width: image.naturalWidth || image.width,
        height: image.naturalHeight || image.height,
      });
    };
    image.onerror = () => {
      setPreview({
        url: objectUrl,
        name: file.name,
        width: 400,
        height: 400,
      });
    };
    image.src = objectUrl;
  }, []);

  const openGalleryPicker = useCallback(() => {
    galleryInputRef.current?.click();
  }, []);

  const openCameraPicker = useCallback(() => {
    cameraInputRef.current?.click();
  }, []);

  const openImage = useCallback((image: GeneratedImage) => {
    setSelectedImage(image);
  }, []);

  const closeImage = useCallback(() => {
    setSelectedImage(null);
  }, []);

  return {
    catalog,
    families: catalog.families,
    catalogLoading,
    catalogError,
    familyId,
    colorId,
    currentFamily,
    isGenerating,
    generationError,
    images,
    selectedImage,
    preview,
    galleryInputRef,
    cameraInputRef,
    selectFamily: handleFamilyChange,
    selectColor: handleColorSelect,
    generate: handleGenerate,
    handleFileSelection,
    openGalleryPicker,
    openCameraPicker,
    openImage,
    closeImage,
  };
}
