export type ColorRead = {
  id: number;
  color_id: string;
  name: string;
  hex_value: string;
  swatch_url?: string | null;
};

export type ColorCreate = Omit<ColorRead, "id">;

export type FabricRead = {
  id: number;
  family_id: string;
  display_name: string;
  status: "active" | "inactive";
  colors: ColorRead[];
};

export type FabricCreate = Omit<FabricRead, "id" | "colors"> & {
  colors?: ColorCreate[];
};
