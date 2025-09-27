import type { NextConfig } from "next";

const RUNPOD_URL = process.env.NEXT_PUBLIC_RUNPOD_URL; // e.g. https://lnqrev4dnktv7s-8000.proxy.runpod.net

const nextConfig: NextConfig = {
    async rewrites() {
    return RUNPOD_URL
      ? [
          // Frontend calls /api/* and Next proxies it to RunPod
          { source: "/api/:path*", destination: `${RUNPOD_URL}/:path*` },
        ]
      : [];
  },

  images: {
    domains: ["picsum.photos"], // 👈 allow this host
    remotePatterns: [
      { protocol: "http", hostname: "localhost", port: "8000", pathname: "/files/**" },
      { protocol: "http", hostname: "127.0.0.1", port: "8000", pathname: "/files/**" },
      { protocol: "https", hostname: "*.proxy.runpod.net" }, // RunPod images

    ],
  },
};

export default nextConfig;
