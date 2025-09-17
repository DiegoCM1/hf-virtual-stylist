"use client";
import { useEffect, useState, useRef } from "react";
import { API_BASE } from "@/lib/api";
import Image from "next/image";
import SearchTela from "@/components/SearchTela";

type Color = {
  color_id: string;
  name: string;
  hex: string;
  swatch_url?: string | null;
};
type Family = {
  family_id: string;
  display_name: string;
  status: "active" | "inactive";
  sort: number;
  colors: Color[];
};
type CatalogResponse = { families: Family[] };

type Cut = "recto" | "cruzado";

export default function Home() {
  const [catalog, setCatalog] = useState<CatalogResponse>({ families: [] });
  const [familyId, setFamilyId] = useState<string>("");
  const [colorId, setColorId] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [images, setImages] = useState<
    { cut: Cut; url: string; width: number; height: number }[]
  >([]);
  const [selected, setSelected] = useState<{
    url: string;
    cut: Cut;
    width: number;
    height: number;
  } | null>(null);
  const [preview, setPreview] = useState<
    { url: string; name: string; width: number; height: number } | null
  >(null);
  const galleryInputRef = useRef<HTMLInputElement | null>(null);
  const cameraInputRef = useRef<HTMLInputElement | null>(null);
  const previewUrlRef = useRef<string | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const res = await fetch(`${API_BASE}/catalog`);
        const data = await res.json();
        setCatalog(data);
        // Preselect first active family/color
        const fam =
          data.families.find((f: Family) => f.status === "active") ||
          data.families[0];
        if (fam) {
          setFamilyId(fam.family_id);
          if (fam.colors?.length) setColorId(fam.colors[0].color_id);
        }
      } catch (err) {
        console.error(err);
        setError("No se pudo cargar el catálogo");
      }
    })();
  }, []);

  // Disable scroll
  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") setSelected(null);
    }
    if (selected) {
      document.addEventListener("keydown", onKey);
      document.body.style.overflow = "hidden";
    }
    return () => {
      document.removeEventListener("keydown", onKey);
      document.body.style.overflow = "";
    };
  }, [selected]);

  const currentFamily = catalog.families.find((f) => f.family_id === familyId);

  useEffect(() => {
    return () => {
      if (previewUrlRef.current) {
        URL.revokeObjectURL(previewUrlRef.current);
      }
    };
  }, []);

  function handlePreview(files: FileList | null) {
    const file = files?.[0];
    if (!file) return;
    if (previewUrlRef.current) {
      URL.revokeObjectURL(previewUrlRef.current);
    }
    const url = URL.createObjectURL(file);
    previewUrlRef.current = url;
    const img = new window.Image();
    img.onload = () => {
      setPreview({
        url,
        name: file.name,
        width: img.naturalWidth || img.width,
        height: img.naturalHeight || img.height,
      });
    };
    img.onerror = () => {
      setPreview({ url, name: file.name, width: 400, height: 400 });
    };
    img.src = url;
  }

  async function onGenerate() {
    setLoading(true);
    setError(null);
    setImages([]);
    try {
      const res = await fetch(`${API_BASE}/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          family_id: familyId,
          color_id: colorId,
          cuts: ["recto", "cruzado"],
          quality: "final",
        }),
      });
      if (!res.ok) throw new Error("API error");
      const data = await res.json();
      setImages(data.images || []);
    } catch (err) {
      console.error(err);
      setError("No pudimos generar las imágenes. Probemos otra combinación.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen max-w-4xl mx-auto p-6">
      <header className="mb-6 flex items-center justify-between">
        <Image
          src="/logo-transparent.webp"
          alt="Harris & Frank logo"
          width={180} // adjust to your design
          height={60}
          priority
        />
      </header>

      <section className="grid gap-4 md:grid-cols-3">
        {/* Left controls */}
        <div className="md:col-span-1 space-y-4">
          <div>
            <label className="text-sm block mb-1">Familia de tela</label>
            <select
              className="border rounded p-2 w-full"
              value={familyId}
              onChange={(e) => {
                setFamilyId(e.target.value);
                setColorId("");
              }}
            >
              {catalog.families.map((f) => (
                <option
                  className="text-black"
                  key={f.family_id}
                  value={f.family_id}
                >
                  {f.display_name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="text-sm block mb-1">Tela</label>
            <div className="grid grid-cols-3 gap-2">
              {currentFamily?.colors?.map((c) => (
                <button
                  key={c.color_id}
                  onClick={() => setColorId(c.color_id)}
                  className={`border rounded p-2 text-sm hover:border-gray-500 ${
                    colorId === c.color_id ? "ring-1 ring-white" : ""
                  }`}
                  title={c.name}
                >
                  <div
                    className="w-full h-10 md:h-14 lg:h-16 rounded mb-1"
                    style={{ backgroundColor: c.hex }}
                  />
                  <div className="truncate">{c.name}</div>
                </button>
              ))}
            </div>
          </div>

          <button
            onClick={onGenerate}
            disabled={loading || !familyId || !colorId}
            className="w-full bg-black text-white py-2 rounded disabled:opacity-50 hover:border hover:border-white"
          >
            {loading ? "Generando..." : "Generar imagenes"}
          </button>

          {error && <div className="text-red-600 text-sm">{error}</div>}

          <div className="w-full flex text-white py-2 justify-center">O</div>

          <SearchTela
            catalog={catalog}
            currentFamilyId={familyId}
            currentColorId={colorId}
            onSelect={(famId, colId) => {
              setFamilyId(famId);
              setColorId(colId);
            }}
            // Later you can inject a real resolver:
            // resolveTelaId={async (telaId) => {
            //   const res = await fetch(`${API_BASE}/catalog/search?color_id=${encodeURIComponent(telaId)}`);
            //   if (!res.ok) return null;
            //   return res.json(); // { familyId, colorId }
            // }}
          />

          <div className="space-y-2">
            <input
              ref={galleryInputRef}
              type="file"
              accept="image/*"
              className="hidden"
              onChange={(event) => {
                handlePreview(event.target.files);
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
                handlePreview(event.target.files);
                event.target.value = "";
              }}
            />
            <div className="flex flex-col gap-2 sm:flex-row">
              <button
                type="button"
                className="w-full rounded border border-white/20 bg-white/10 px-3 py-2 text-sm text-white hover:bg-white/20"
                onClick={() => galleryInputRef.current?.click()}
              >
                Elegir foto
              </button>
              <button
                type="button"
                className={[
                  "w-full rounded border border-white/20 bg-white/10 px-3 py-2 text-sm text-white hover:bg-white/20",
                  "md:hidden",
                ].join(" ")}
                onClick={() => cameraInputRef.current?.click()}
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
        </div>

        {/* Right preview */}
        <div className="md:col-span-2">
          {images.length === 0 && !loading && (
            <div className="border rounded p-6 text-neutral-500">
              Elige familia y color, luego presiona Generar.
            </div>
          )}

          {/* Loading state */}
          {loading && (
            <div className="border rounded p-6 text-neutral-600 space-y-2">
              <div className="animate-pulse text-white">
                Inicializando modelo…
              </div>
              <div className="animate-pulse text-white">
                Aplicando textura de tela…
              </div>
              <div className="animate-pulse text-white">
                Renderizando vistas recto y cruzado…
              </div>
            </div>
          )}

          {/* Generated images */}
          {images.length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {images.map((img) => (
                <figure key={img.cut} className="border rounded p-2">
                  <Image
                    src={img.url}
                    alt={img.cut}
                    width={img.width || 800}
                    height={img.height || 1200}
                    className="w-full h-auto rounded cursor-zoom-in"
                    sizes="(min-width: 768px) 50vw, 100vw"
                    onClick={() => setSelected(img)}
                  />
                  <figcaption className="text-sm mt-1 capitalize">
                    {img.cut}
                  </figcaption>
                </figure>
              ))}
            </div>
          )}
        </div>
      </section>

      {/* Modal */}
      {selected && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center"
          aria-modal="true"
          role="dialog"
        >
          {/* Backdrop (click to close) */}
          <div
            className="absolute inset-0 bg-black/70"
            onClick={() => setSelected(null)}
          />

          {/* Dialog */}
          <div
            className="relative max-w-5xl w-[92vw] md:w-auto p-0"
            onClick={(e) => e.stopPropagation()} // prevent closing when clicking image
          >
            {/* Close button (optional but handy) */}
            <button
              aria-label="Cerrar"
              className="absolute -top-10 right-0 md:top-2 md:-right-10 bg-white/10 hover:bg-white/20 text-white rounded-full px-3 py-1 text-sm"
              onClick={() => setSelected(null)}
            >
              ✕
            </button>

            {/* The image */}
            <Image
              src={selected.url}
              alt={selected.cut}
              width={selected.width || 1200}
              height={selected.height || 1600}
              className="rounded shadow-lg max-h-[85vh] w-auto h-auto"
              // If your source images are already optimized or huge/remote and
              // you want to bypass optimization, you can add: unoptimized
              // unoptimized
              sizes="85vh"
              priority
            />
            <div className="mt-2 text-center text-sm text-white/80 capitalize">
              {selected.cut} · Toca fuera para cerrar
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
