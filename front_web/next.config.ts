import type { NextConfig } from "next";

const IMAGE_PROTOCOL = process.env.NEXT_PUBLIC_IMAGE_PROTOCOL || "https";
const IMAGE_HOSTNAME = process.env.NEXT_PUBLIC_IMAGE_HOSTNAME || "public-insight.co.kr";
const IMAGE_HOSTNAME_WWW = process.env.NEXT_PUBLIC_IMAGE_HOSTNAME_WWW || "www.public-insight.co.kr";

const nextConfig: NextConfig = {
  eslint: {
    ignoreDuringBuilds: true,
  },
  output: "standalone",
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "publicinsight.site",
      },
      {
        protocol: "https",
        hostname: "www.publicinsight.site",
      },
      {
        protocol: "https",
        hostname: "public-insight.co.kr",
      },
      {
        protocol: "https",
        hostname: "www.public-insight.co.kr",
      },
    ],
  },
};

export default nextConfig;
