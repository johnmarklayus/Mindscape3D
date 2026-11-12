/** Prose docs: one Markdown file per section under src/content/docs, ordered by filename. */

export interface DocSection {
  id: string
  /** Sidebar group heading. */
  group: string
  /** Sidebar label. */
  nav: string
  body: string
}

export interface NavGroup {
  title: string
  items: { href: string; label: string }[]
}

const files = import.meta.glob<string>("../content/docs/*.md", {
  query: "?raw",
  import: "default",
  eager: true,
})

function parse(file: string, raw: string): DocSection {
  const match = /^---\n([\s\S]*?)\n---\n([\s\S]*)$/.exec(raw.replace(/\r\n/g, "\n"))
  if (!match) throw new Error(`${file}: missing front matter`)
  const fields = Object.fromEntries(
    match[1].split("\n").map((line) => {
      const i = line.indexOf(":")
      return [line.slice(0, i).trim(), line.slice(i + 1).trim()]
    }),
  )
  for (const key of ["id", "group", "nav"]) {
    if (!fields[key]) throw new Error(`${file}: front matter is missing "${key}"`)
  }
  return { id: fields.id, group: fields.group, nav: fields.nav, body: match[2].trim() }
}

export const docSections: DocSection[] = Object.entries(files)
  .sort(([a], [b]) => a.localeCompare(b))
  .map(([file, raw]) => parse(file, raw))

export const docNavGroups: NavGroup[] = []
for (const s of docSections) {
  let group = docNavGroups.find((g) => g.title === s.group)
  if (!group) docNavGroups.push((group = { title: s.group, items: [] }))
  group.items.push({ href: `#${s.id}`, label: s.nav })
}
