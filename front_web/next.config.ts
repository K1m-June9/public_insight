import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  eslint: { ignoreDuringBuilds: true },
  output: 'standalone',
  // 이미지 파일 전송을 위해서 설정, 실제 환경에서는 실제 환경에 대한 protocol, hostname, port, pathname(이건 그대로겠지만)을 작성해야함
  images: {
    remotePatterns: [
      {
        protocol: process.env.NEXT_PUBLIC_IMAGE_PROTOCOL,
        hostname: process.env.NEXT_PUBLIC_IMAGE_HOSTNAME,
        port: process.env.NEXT_PUBLIC_IMAGE_PORT || '', // port는 비어있을 수 있으므로 기본값 설정
        pathname: process.env.NEXT_PUBLIC_IMAGE_PATHNAME,
      },
    ],
  },
};

export default nextConfig;
