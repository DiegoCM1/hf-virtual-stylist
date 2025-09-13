"use client";
import { useEffect, useState } from "react";
import { API_BASE } from "@/lib/api";

type Color = { color_id: string; name: string; hex: string; swatch_url?: string | null };
type Family = { family_id: string; display_name: string; status: "active"|"inactive"; sort: number; colors: Color[] };
type CatalogResponse = { families: Family[] };

type Cut = "recto" | "cruzado";

export default function Home() {
  const [catalog, setCatalog] = useState<CatalogResponse>({ families: [] });
  const [familyId, setFamilyId] = useState<string>("");
  const [colorId, setColorId] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string|null>(null);
  const [images, setImages] = useState<{cut: Cut; url: string; width: number; height: number}[]>([]);

  useEffect(() => {
    (async () => {
      try {
        const res = await fetch(`${API_BASE}/catalog`);
        const data = await res.json();
        setCatalog(data);
        // Preselect first active family/color
        const fam = data.families.find((f: Family) => f.status === "active") || data.families[0];
        if (fam) {
          setFamilyId(fam.family_id);
          if (fam.colors?.length) setColorId(fam.colors[0].color_id);
        }
      } catch (e:any) {
        console.error(e);
        setError("No se pudo cargar el catálogo");
      }
    })();
  }, []);

  const currentFamily = catalog.families.find(f => f.family_id === familyId);

  async function onGenerate() {
    setLoading(true); setError(null); setImages([]);
    try {
      const res = await fetch(`${API_BASE}/generate`, {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({
          family_id: familyId,
          color_id: colorId,
          cuts: ["recto","cruzado"],
          quality: "final"
        })
      });
      if (!res.ok) throw new Error("API error");
      const data = await res.json();
      setImages(data.images || []);
    } catch (e:any) {
      setError("No pudimos generar las imágenes. Probemos otra combinación.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen max-w-4xl mx-auto p-6">
      <header className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-semibold">HF Virtual Stylist</h1>
        <div className="text-sm text-neutral-500">Demo · Semana 1</div>
      </header>

      <section className="grid gap-4 md:grid-cols-3">
        {/* Left controls */}
        <div className="md:col-span-1 space-y-4">
          <div>
            <label className="text-sm block mb-1">Familia de tela</label>
            <select
              className="border rounded p-2 w-full"
              value={familyId}
              onChange={(e)=>{ setFamilyId(e.target.value); setColorId(""); }}
            >
              {catalog.families.map(f=>(
                <option key={f.family_id} value={f.family_id}>{f.display_name}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="text-sm block mb-1">Color</label>
            <div className="grid grid-cols-3 gap-2">
              {currentFamily?.colors?.map(c=>(
                <button
                  key={c.color_id}
                  onClick={()=>setColorId(c.color_id)}
                  className={`border rounded p-2 text-sm hover:border-gray-500 ${colorId === c.color_id ? "ring-2 ring-black" : ""}`}
                  title={c.name}
                >
                  <div className="w-full h-6 rounded mb-1" style={{backgroundColor: c.hex}} />
                  <div className="truncate">{c.name}</div>
                </button>
              ))}
            </div>
          </div>

          <button
            onClick={onGenerate}
            disabled={loading || !familyId || !colorId}
            className="w-full bg-black text-white py-2 rounded disabled:opacity-50 hover:border-white"
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
              <div className="animate-pulse text-white">Inicializando modelo…</div>
              <div className="animate-pulse text-white">Aplicando textura de tela…</div>
              <div className="animate-pulse text-white">Renderizando vistas recto y cruzado…</div>
            </div>
          )}

          {images.length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {images.map(img=>(
                <figure key={img.cut} className="border rounded p-2">
                  <img src={img.url} alt={img.cut} className="w-full h-auto rounded" />
                  <figcaption className="text-sm mt-1 capitalize">{img.cut}</figcaption>
                </figure>
              ))}
            </div>
          )}
        </div>
      </section>
    </main>
  );
}
