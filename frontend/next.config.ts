// frontend/next.config.ts 또는 next.config.mjs
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async headers() {
    return [
      {
        source: "/(.*)",
        headers: [
          {
            key: "Cross-Origin-Opener-Policy",
            value: "same-origin-allow-popups", // 👈 팝업창과의 교차 출처 통신을 허용합니다.
          },
        ],
      },
    ];
  },
};

export default nextConfig;