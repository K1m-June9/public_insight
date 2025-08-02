import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  eslint: { ignoreDuringBuilds: true },
  output: 'standalone',
  // 이미지 파일 전송을 위해서 설정, 실제 환경에서는 실제 환경에 대한 protocol, hostname, port, pathname(이건 그대로겠지만)을 작성해야함
  images: {
    remotePatterns: [
      {
        protocol: 'http',
        hostname: 'localhost',
        port: '8001',
        pathname: '/static/**', // /static/으로 시작하는 모든 경로 허용
      },
    ],
  },
};

export default nextConfig;
