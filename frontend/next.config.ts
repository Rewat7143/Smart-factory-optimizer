import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  allowedDevOrigins: [
    '192.168.0.101',
    '192.168.0.101:3000',
    '172.24.132.35',
    '172.24.132.35:3000',
    'localhost:3000',
    '127.0.0.1:3000'
  ],
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://127.0.0.1:8000/api/:path*',
      },
    ];
  },
};

export default nextConfig;
