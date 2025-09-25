import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    domains: ["picsum.photos"], // 👈 allow this host
    remotePatterns: [
      { protocol: "http", hostname: "localhost", port: "8000", pathname: "/files/**" },
      { protocol: "http", hostname: "127.0.0.1", port: "8000", pathname: "/files/**" },
    ],
  },
};

export default nextConfig;
