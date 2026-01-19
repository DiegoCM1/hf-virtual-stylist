import { Family } from "@/types/catalog";
import Image from "next/image";

type CatalogSelectorProps = {
  families: Family[];
  selectedFamilyId: string;
  selectedColorId: string;
  onFamilyChange: (familyId: string) => void;
  onColorSelect: (colorId: string) => void;
  hasCustomSwatch?: boolean;
};

export function CatalogSelector({
  families,
  selectedFamilyId,
  selectedColorId,
  onFamilyChange,
  onColorSelect,
  hasCustomSwatch = false,
}: CatalogSelectorProps) {
  const activeFamily = families.find((family) => family.family_id === selectedFamilyId);

  return (
    <div>
      <label className="text-sm block mb-2 font-body text-gray-700">Tela</label>
        {/* Fixed grid showing exactly 2 rows x 4 columns (8 items) */}
        <div className="overflow-y-auto border border-gray-300 rounded-[3px] p-4 bg-white shadow-sm" style={{ maxHeight: 'calc((100vh - 400px) * 0.67)', minHeight: '280px' }}>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3 auto-rows-min">
            {activeFamily?.colors?.map((color) => (
              <button
                key={color.color_id}
                onClick={() => onColorSelect(color.color_id)}
                className={`border rounded-[3px] p-3 text-sm hover:border-gray-900 hover:shadow-md transition-all duration-200 group ${
                  selectedColorId === color.color_id && !hasCustomSwatch
                    ? "ring-2 ring-gray-900 ring-offset-2 border-gray-900 shadow-md"
                    : "border-gray-300 bg-white"
                }`}
                title={color.name}
                type="button"
              >
                {color.swatch_url ? (
                  <div className="relative w-full aspect-square rounded-[3px] overflow-hidden mb-2 bg-gray-100">
                    <Image
                      src={color.swatch_url}
                      alt={color.name}
                      fill
                      className="object-cover group-hover:scale-105 transition-transform duration-200"
                      sizes="(max-width: 640px) 50vw, (max-width: 1024px) 33vw, 20vw"
                    />
                  </div>
                ) : (
                  <div
                    className="w-full aspect-square rounded-[3px] mb-2"
                    style={{ backgroundColor: color.hex }}
                  />
                )}
                <div className="truncate text-xs font-body text-gray-900">{color.name}</div>
              </button>
            ))}
          </div>
        </div>
    </div>
  );
}
