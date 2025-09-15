import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    domains: ["picsum.photos"], // 👈 allow this host
  },
};

export default nextConfig;
