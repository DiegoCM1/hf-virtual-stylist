// Luxury fonts configuration - Harris & Frank inspired
import { Figtree, Jost } from "next/font/google";

// Figtree - For headers with elegant letter-spacing
export const figtree = Figtree({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  variable: "--font-figtree",
  display: "swap",
});

// Jost - For body text with refined readability
export const jost = Jost({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  variable: "--font-jost",
  display: "swap",
});
