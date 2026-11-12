import type { Metadata, Viewport } from "next"
import { Comic_Neue, STIX_Two_Text } from "next/font/google"
import type { ReactNode } from "react"
import { Provider } from "@/components/provider"
import { site } from "@/lib/site"

// The game's two typefaces: a book serif for titles (Story Serif / STIX) and Comic Neue for everything else.
const story = STIX_Two_Text({ subsets: ["latin"], variable: "--font-story", display: "swap" })
const body = Comic_Neue({ subsets: ["latin"], weight: ["300", "400", "700"], variable: "--font-body", display: "swap" })

export const metadata: Metadata = {
  metadataBase: new URL(site.url),
  title: { default: `${site.name}: ${site.tagline}`, template: `%s · ${site.name}` },
  description: site.description,
  applicationName: site.name,
  keywords: site.keywords,
  authors: [{ name: "The MindScape 3D Team" }],
  creator: "The MindScape 3D Team",
  category: "games",
  alternates: { canonical: "/" },
  openGraph: {
    type: "website",
    siteName: site.name,
    title: `${site.name}: ${site.tagline}`,
    description: site.description,
    url: "/",
    locale: "en_PH",
  },
  twitter: { card: "summary_large_image", title: `${site.name}: ${site.tagline}`, description: site.description },
  robots: { index: true, follow: true, googleBot: { index: true, follow: true, "max-image-preview": "large" } },
  formatDetection: { telephone: false },
}

export const viewport: Viewport = {
  themeColor: "#12181b",
  colorScheme: "dark",
}

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" className={`dark ${story.variable} ${body.variable}`} style={{ colorScheme: "dark" }}>
      <body>
        <Provider>{children}</Provider>
      </body>
    </html>
  )
}
