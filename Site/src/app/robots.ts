import type { MetadataRoute } from "next"
import { site } from "@/lib/site"

// Preview deployments (VERCEL_ENV=preview) are kept out of search results; production is open to all crawlers.
export default function robots(): MetadataRoute.Robots {
  if (process.env.VERCEL_ENV === "preview") return { rules: { userAgent: "*", disallow: "/" } }
  return {
    rules: { userAgent: "*", allow: "/", disallow: ["/api/", "/game/"] },
    sitemap: `${site.url}/sitemap.xml`,
    host: site.url,
  }
}
