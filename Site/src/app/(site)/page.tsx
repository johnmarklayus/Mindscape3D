import { About } from "@/components/about"
import { Contact } from "@/components/contact"
import { Downloads } from "@/components/downloads"
import { Hero } from "@/components/hero"
import { Chapters, Features, Overview } from "@/components/overview"
import { downloads } from "@/data/downloads"
import { site } from "@/lib/site"

// Structured data so search engines can show the game, its platforms and the site name in results.
function JsonLd() {
  const data = [
    {
      "@context": "https://schema.org",
      "@type": "VideoGame",
      name: site.name,
      alternateName: site.fullTitle,
      description: site.description,
      url: site.url,
      image: `${site.url}/opengraph-image.jpg`,
      genre: ["Adventure", "Simulation", "Serious game"],
      gamePlatform: ["Windows", "macOS", "Android", "Web browser"],
      operatingSystem: "Windows 10+, macOS 12+, Android 8.0+, modern web browsers",
      applicationCategory: "GameApplication",
      playMode: "SinglePlayer",
      inLanguage: "en",
      softwareVersion: site.version,
      audience: { "@type": "PeopleAudience", suggestedMinAge: 18, audienceType: "Young adults" },
      offers: { "@type": "Offer", price: "0", priceCurrency: "PHP", availability: "https://schema.org/InStock" },
      author: { "@type": "Organization", name: "The MindScape 3D Team" },
      publisher: { "@type": "EducationalOrganization", name: site.institution },
      downloadUrl: downloads.filter((d) => d.url && d.id !== "web").map((d) => d.url),
    },
    {
      "@context": "https://schema.org",
      "@type": "WebSite",
      name: site.name,
      url: site.url,
    },
  ]
  return <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(data).replace(/</g, "\\u003c") }} />
}

export default function Home() {
  return (
    <>
      <JsonLd />
      <Hero />
      <Overview />
      <Features />
      <Chapters />
      <Downloads />
      <About />
      <Contact />
    </>
  )
}
