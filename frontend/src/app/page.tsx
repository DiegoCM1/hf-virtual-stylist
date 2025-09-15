"use client";
import { useEffect, useState } from "react";
import { API_BASE } from "@/lib/api";
import Image from "next/image";

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
      } catch (e: any) {
        console.error(e);
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
    } catch (e: any) {
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
            <label className="text-sm block mb-1">Color</label>
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
                    className="w-full h-6 rounded mb-1"
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
        </div>

        {/* Right preview */}
        <div className="md:col-span-2">
          {images.length === 0 && !loading && (
            <div className="border rounded p-6 text-neutral-500">
              Elige familia y color, luego presiona Generar.
            </div>
          )}

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

          {images.length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {images.map((img) => (
                <figure key={img.cut} className="border rounded p-2">
                  {/* Use Next/Image instead of <img> */}
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
              {selected.cut} · clic fuera para cerrar
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
