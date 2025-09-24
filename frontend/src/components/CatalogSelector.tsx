import { Family } from "@/types/catalog";

type CatalogSelectorProps = {
  families: Family[];
  selectedFamilyId: string;
  selectedColorId: string;
  onFamilyChange: (familyId: string) => void;
  onColorSelect: (colorId: string) => void;
};

export function CatalogSelector({
  families,
  selectedFamilyId,
  selectedColorId,
  onFamilyChange,
  onColorSelect,
}: CatalogSelectorProps) {
  const activeFamily = families.find((family) => family.family_id === selectedFamilyId);

  return (
    <div className="space-y-4">
      <div>
        <label className="text-sm block mb-1">Familia de tela</label>
        <select
          className="border rounded p-2 w-full"
          value={selectedFamilyId}
          onChange={(event) => onFamilyChange(event.target.value)}
        >
          {families.map((family) => (
            <option className="text-black" key={family.family_id} value={family.family_id}>
              {family.display_name}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label className="text-sm block mb-1">Tela</label>
        <div className="grid grid-cols-3 gap-2">
          {activeFamily?.colors?.map((color) => (
            <button
              key={color.color_id}
              onClick={() => onColorSelect(color.color_id)}
              className={`border rounded p-2 text-sm hover:border-gray-500 ${
                selectedColorId === color.color_id ? "ring-1 ring-white" : ""
              }`}
              title={color.name}
              type="button"
            >
              <div
                className="w-full h-10 md:h-14 lg:h-16 rounded mb-1"
                style={{ backgroundColor: color.hex }}
              />
              <div className="truncate">{color.name}</div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
