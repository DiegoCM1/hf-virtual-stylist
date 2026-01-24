import type { NextConfig } from "next";

const RAW_API_BASE = process.env.NEXT_PUBLIC_API_BASE;
const API_BASE = RAW_API_BASE ? RAW_API_BASE.replace(/\/+$/, "") : undefined;

const nextConfig: NextConfig = {
    async rewrites() {
    return API_BASE
      ? [
          // Frontend calls /api/* and Next proxies it to RunPod
          { source: "/api/:path*", destination: `${API_BASE}/:path*` },
        ]
      : [];
  },

  images: {
    remotePatterns: [
      // Local development
      { protocol: "http", hostname: "localhost", port: "8000", pathname: "/files/**" },
      { protocol: "http", hostname: "127.0.0.1", port: "8000", pathname: "/files/**" },
      // Production backends
      { protocol: "https", hostname: "*.proxy.runpod.net" }, // RunPod images
      { protocol: "https", hostname: "*.railway.app" }, // Railway backend
      { protocol: "https", hostname: "hf-virtual-stylist-production.up.railway.app" }, // Railway production
      // Storage backends
      { protocol: "https", hostname: "*.r2.dev" }, // Cloudflare R2 (allows any R2 public bucket)
    ],
  },
};

export default nextConfig;
