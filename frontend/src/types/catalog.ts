export type Color = {
  color_id: string;
  name: string;
  hex: string;
  swatch_url?: string | null;
};

export type Family = {
  family_id: string;
  display_name: string;
  status: "active" | "inactive";
  sort: number;
  colors: Color[];
};

export type CatalogResponse = {
  families: Family[];
};

export type Cut = "recto" | "cruzado";

export type GeneratedImage = {
  cut: Cut;
  url: string;
  width: number;
  height: number;
};

export type PreviewImage = {
  url: string;
  name: string;
  width: number;
  height: number;
};

export type ColorSelection = {
  familyId: string;
  colorId: string;
};
