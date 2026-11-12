import type { NextConfig } from "next"

// The WebGL build is Brotli-compressed without Unity's decompression fallback, so the browser must be told the
// .br files are compressed (Content-Encoding: br) and what they contain, or the game fails to start.
const unityBuild = [
  { source: "/game/Build/:file*.js.br", type: "application/javascript" },
  { source: "/game/Build/:file*.wasm.br", type: "application/wasm" },
  { source: "/game/Build/:file*.data.br", type: "application/octet-stream" },
].map(({ source, type }) => ({
  source,
  headers: [
    { key: "Content-Encoding", value: "br" },
    { key: "Content-Type", value: type },
    { key: "Cache-Control", value: "public, max-age=86400, must-revalidate" },
  ],
}))

const security = [
  { key: "X-Content-Type-Options", value: "nosniff" },
  { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
  { key: "X-Frame-Options", value: "SAMEORIGIN" },
  { key: "Permissions-Policy", value: "camera=(), microphone=(), geolocation=()" },
]

const config: NextConfig = {
  // This folder is the app root (there are other lockfiles further up the disk).
  turbopack: { root: __dirname },
  reactStrictMode: true,
  poweredByHeader: false,
  images: { formats: ["image/avif", "image/webp"], qualities: [75, 85] },
  experimental: { optimizePackageImports: ["@chakra-ui/react", "react-icons"] },
  // The Privacy Policy and Terms are a modal now (#privacy, #terms); old links still land on them.
  async redirects() {
    return [
      { source: "/privacy", destination: "/#privacy", permanent: true },
      { source: "/terms", destination: "/#terms", permanent: true },
    ]
  },
  async headers() {
    return [{ source: "/:path*", headers: security }, ...unityBuild]
  },
}

export default config
