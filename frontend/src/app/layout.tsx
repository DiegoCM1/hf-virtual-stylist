import type { Metadata } from "next";
import { figtree, jost } from "@/lib/fonts";
import "./globals.css";

export const metadata: Metadata = {
  title: "HF - Estilista Virtual",
  description: "The AI engine powering Harris & Frank's infinite digital showroom. It uses custom models trained on exclusive fabrics to generate hyper-realistic, bespoke suits on-demand, transforming any sales conversation into an instant, interactive design session.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${figtree.variable} ${jost.variable} font-sans antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
