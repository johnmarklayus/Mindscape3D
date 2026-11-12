// The download cards. To publish a new build: upload it, put its link in the matching NEXT_PUBLIC_DOWNLOAD_* variable
// (Vercel > Settings > Environment Variables), and update version, date and size here.

// While developing (`npm run dev`), a platform without a variable falls back to the local build linked into
// public/downloads by scripts/link-downloads.mjs. Production builds only ever use the variables.
const devFile = (name: string) => (process.env.NODE_ENV === "development" ? `/downloads/${name}` : "")

export type PlatformId = "windows" | "macos" | "android" | "web"

export type Requirements = { label: string; value: string }[]

export type Download = {
  id: PlatformId
  name: string
  file: string
  version: string
  date: string
  size: string
  url: string
  note?: string
  minimum: Requirements
  recommended: Requirements
}

export const downloads: Download[] = [
  {
    id: "windows",
    name: "Windows",
    file: "Mindscape-Windows-2026-11-12.zip",
    version: "0.3.0",
    date: "2026-11-12",
    size: "189 MB",
    url: process.env.NEXT_PUBLIC_DOWNLOAD_WINDOWS || devFile("Mindscape-Windows.zip"),
    note: "Unzip, then open Windows/Mindscape.exe (keep the files beside it).",
    minimum: [
      { label: "OS", value: "Windows 10 (64-bit), version 21H1 or later" },
      { label: "Processor", value: "x64 dual-core, 2.0 GHz with SSE2" },
      { label: "Memory", value: "4 GB RAM" },
      { label: "Graphics", value: "DirectX 11 GPU (Intel UHD 620 or similar)" },
      { label: "Storage", value: "1 GB free space" },
    ],
    recommended: [
      { label: "OS", value: "Windows 11 (64-bit)" },
      { label: "Processor", value: "Quad-core, 3.0 GHz (Intel Core i5 / AMD Ryzen 5)" },
      { label: "Memory", value: "8 GB RAM" },
      { label: "Graphics", value: "GTX 1050 / RX 560 or Intel Iris Xe" },
      { label: "Storage", value: "2 GB free space (SSD)" },
    ],
  },
  {
    id: "macos",
    name: "macOS",
    file: "Mindscape-macOS-2026-11-12.zip",
    version: "0.3.0",
    date: "2026-11-12",
    size: "174 MB",
    url: process.env.NEXT_PUBLIC_DOWNLOAD_MACOS || devFile("Mindscape-macOS.zip"),
    note: "Apple silicon Macs. Unzip, then right-click Mindscape and choose Open the first time.",
    minimum: [
      { label: "OS", value: "macOS 12 Monterey" },
      { label: "Processor", value: "Apple M1" },
      { label: "Memory", value: "8 GB unified memory" },
      { label: "Graphics", value: "Metal (built into Apple silicon)" },
      { label: "Storage", value: "1 GB free space" },
    ],
    recommended: [
      { label: "OS", value: "macOS 14 Sonoma or later" },
      { label: "Processor", value: "Apple M2 or newer" },
      { label: "Memory", value: "16 GB unified memory" },
      { label: "Graphics", value: "Metal (built into Apple silicon)" },
      { label: "Storage", value: "2 GB free space" },
    ],
  },
  {
    id: "android",
    name: "Android",
    file: "Mindscape-2026-11-12.apk",
    version: "0.3.0",
    date: "2026-11-12",
    size: "188 MB",
    url: process.env.NEXT_PUBLIC_DOWNLOAD_ANDROID || devFile("Mindscape.apk"),
    note: "Allow installs from your browser when Android asks, then open the APK.",
    minimum: [
      { label: "OS", value: "Android 8.0 (Oreo, API 26)" },
      { label: "Processor", value: "64-bit ARM (arm64-v8a)" },
      { label: "Memory", value: "3 GB RAM" },
      { label: "Graphics", value: "OpenGL ES 3.0 or Vulkan" },
      { label: "Storage", value: "600 MB free space" },
    ],
    recommended: [
      { label: "OS", value: "Android 12 or later" },
      { label: "Processor", value: "Snapdragon 7-series / Dimensity 7000 or better" },
      { label: "Memory", value: "6 GB RAM" },
      { label: "Graphics", value: "Vulkan" },
      { label: "Storage", value: "1 GB free space" },
    ],
  },
  {
    id: "web",
    name: "Web browser",
    file: "Play online, no install",
    version: "0.3.0",
    date: "2026-11-11",
    size: "≈ 108 MB first load",
    url: "/play",
    note: "Loads once, then your browser keeps it. Works best on a desktop or laptop.",
    minimum: [
      { label: "Browser", value: "Latest Chrome, Edge, Firefox or Safari with WebGL 2" },
      { label: "Device", value: "Desktop or laptop, dual-core CPU" },
      { label: "Memory", value: "8 GB RAM" },
      { label: "Graphics", value: "Integrated graphics with WebGL 2" },
      { label: "Connection", value: "10 Mbps for the first load" },
    ],
    recommended: [
      { label: "Browser", value: "Latest Chrome or Edge" },
      { label: "Device", value: "Desktop or laptop, quad-core CPU" },
      { label: "Memory", value: "16 GB RAM" },
      { label: "Graphics", value: "Dedicated GPU or Apple silicon" },
      { label: "Connection", value: "25 Mbps or faster" },
    ],
  },
]
