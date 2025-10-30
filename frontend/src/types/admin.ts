export type ColorRead = {
  id: number;
  color_id: string;
  name: string;
  hex_value: string;
  swatch_code?: string | null;
  swatch_url?: string | null;
  status: "active" | "inactive";
  fabric_family_id: number;
  created_at: string;
  updated_at: string;
};

export type ColorCreate = Omit<ColorRead, "id" | "fabric_family_id" | "created_at" | "updated_at">;

export type ColorUpdate = Partial<Omit<ColorRead, "id" | "created_at" | "updated_at">> & {
  fabric_family_id?: number; // For moving colors between families
};

export type FabricRead = {
  id: number;
  family_id: string;
  display_name: string;
  status: "active" | "inactive";
  colors: ColorRead[];
  created_at: string;
  updated_at: string;
};

export type FabricCreate = Omit<FabricRead, "id" | "colors" | "created_at" | "updated_at"> & {
  colors?: ColorCreate[];
};

export type GenerationJobRead = {
  id: number;
  job_id: string;
  status: "pending" | "processing" | "completed" | "failed";
  family_id: string;
  color_id: string;
  cuts: string[];
  seed?: number | null;
  result_urls?: string[] | null;
  error_message?: string | null;
  created_at: string;
  updated_at: string;
  started_at?: string | null;
  completed_at?: string | null;
};
