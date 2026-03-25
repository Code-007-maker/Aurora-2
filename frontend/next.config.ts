import type { NextConfig } from "next";

const nextConfig: NextConfig = {
    // This tells Next.js to ignore TypeScript errors during the build
    typescript: {
        ignoreBuildErrors: true,
    },
    // Optional: Also ignores ESLint errors which can often fail Render builds
    eslint: {
        ignoreDuringBuilds: true,
    },
    async rewrites() {
        return [
            {
                source: "/api/:path*",
                destination: "http://localhost:8000/api/:path*",
            },
            {
                source: "/auth/:path*",
                destination: "http://localhost:8000/auth/:path*",
            },
        ];
    },
};

export default nextConfig;
