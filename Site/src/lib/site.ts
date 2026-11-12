// One place for the site's name, address and shared copy. Change the domain with NEXT_PUBLIC_SITE_URL.

const vercelUrl = process.env.VERCEL_PROJECT_PRODUCTION_URL ? `https://${process.env.VERCEL_PROJECT_PRODUCTION_URL}` : undefined

export const site = {
  name: "MindScape 3D",
  shortName: "MindScape",
  tagline: "Face Your Fear, Find Your Strength.",
  fullTitle:
    "A Cross-Platform Online Interactive Simulation Game for Emotional Awareness and Coping Skill Development for Young Adults",
  description:
    "MindScape 3D is a free story game about the everyday pressures young adults face. Explore home, school and the city as Joey, make choices, and practise calming skills like guided breathing, grounding and reframing worried thoughts. Play in your browser or download for Windows, macOS and Android.",
  url: (process.env.NEXT_PUBLIC_SITE_URL || vercelUrl || "http://localhost:3000").replace(/\/$/, ""),
  version: "0.3.0",
  updated: "2026-11-12",
  institution: "STI College Global City",
  contactEmail: process.env.NEXT_PUBLIC_CONTACT_EMAIL || "",
  gameUrl: (process.env.NEXT_PUBLIC_GAME_URL || "/game").replace(/\/$/, ""),
  keywords: [
    "MindScape 3D",
    "mental health game",
    "emotional awareness",
    "coping skills",
    "stress management game",
    "academic pressure",
    "young adults",
    "serious game",
    "breathing exercise",
    "CBT game",
    "WebGL game",
    "Philippines",
  ],
}

export const nav = [
  { label: "Overview", href: "/#overview" },
  { label: "Features", href: "/#features" },
  { label: "Chapters", href: "/#chapters" },
  { label: "Download", href: "/#download" },
  { label: "About", href: "/#about" },
  { label: "Contact", href: "/#contact" },
]
