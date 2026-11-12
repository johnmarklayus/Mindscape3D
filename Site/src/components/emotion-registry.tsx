"use client"

import createCache from "@emotion/cache"
import { CacheProvider } from "@emotion/react"
import { useServerInsertedHTML } from "next/navigation"
import { useState, type ReactNode } from "react"

// Chakra UI styles with Emotion. In the App Router, Emotion would otherwise write <style> tags inside the page while
// rendering on the server, which React then finds out of place on the client (a hydration error). This collects every
// style made during the server render and puts it in the document <head> instead.
export function EmotionRegistry({ children }: { children: ReactNode }) {
  const [registry] = useState(() => {
    const cache = createCache({ key: "css" })
    cache.compat = true
    const insert = cache.insert
    let inserted: { name: string; isGlobal: boolean }[] = []
    cache.insert = (...args) => {
      const [selector, serialized] = args
      if (cache.inserted[serialized.name] === undefined) inserted.push({ name: serialized.name, isGlobal: !selector })
      return insert(...args)
    }
    const flush = () => {
      const out = inserted
      inserted = []
      return out
    }
    return { cache, flush }
  })

  useServerInsertedHTML(() => {
    const names = registry.flush()
    if (names.length === 0) return null
    let styles = ""
    let attr = registry.cache.key
    const globals: { name: string; style: string }[] = []
    for (const { name, isGlobal } of names) {
      const style = registry.cache.inserted[name]
      if (typeof style !== "string") continue
      if (isGlobal) globals.push({ name, style })
      else {
        styles += style
        attr += ` ${name}`
      }
    }
    return (
      <>
        {globals.map(({ name, style }) => (
          <style key={name} data-emotion={`${registry.cache.key}-global ${name}`} dangerouslySetInnerHTML={{ __html: style }} />
        ))}
        {styles && <style data-emotion={attr} dangerouslySetInnerHTML={{ __html: styles }} />}
      </>
    )
  })

  return <CacheProvider value={registry.cache}>{children}</CacheProvider>
}
