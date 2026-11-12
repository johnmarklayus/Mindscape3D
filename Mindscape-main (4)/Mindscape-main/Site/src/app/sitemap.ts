import type { MetadataRoute } from "next"
import { site } from "@/lib/site"

export default function sitemap(): MetadataRoute.Sitemap {
  const updated = new Date(`${site.updated}T00:00:00Z`)
  return [
    { url: `${site.url}/`, lastModified: updated, changeFrequency: "monthly", priority: 1 },
    { url: `${site.url}/play`, lastModified: updated, changeFrequency: "monthly", priority: 0.8 },
  ]
}
