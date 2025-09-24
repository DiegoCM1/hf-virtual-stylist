import { ColorSelection } from "@/types/catalog";

export type SearchStatus = "idle" | "ok" | "notfound" | "already" | "loading";

export type ResolveTelaResult = ColorSelection | null;
