/**
 * Script docs. The C# comes from copies of the Unity scripts in src/content/code/ (loaded lazily as
 * raw text), and the annotations live in src/content/scripts/<id>.json. Notes are anchored to a line's
 * trimmed text rather than a line number, so editing a script doesn't shift them onto the wrong line.
 */

export interface ScriptNote {
  /** Trimmed text of the first line the note applies to. */
  match: string
  /** Which occurrence of `match` to use (1-based); omit when the line is unique. */
  nth?: number
  /** How many lines the note covers, starting at the match; defaults to 1. */
  span?: number
  text: string
}

export interface ScriptMeta {
  id: string
  title: string
  path: string
  summary: string
  notes: ScriptNote[]
}

const metaModules = import.meta.glob<ScriptMeta | string[]>("../content/scripts/*.json", {
  eager: true,
  import: "default",
})

// Copies of the Unity scripts, kept in sync from Assets/ by scripts/sync-code.mjs.
const sourceLoaders = import.meta.glob<string>("../content/code/**/*.cs", {
  query: "?raw",
  import: "default",
})

const metaById = new Map<string, ScriptMeta>()
for (const [file, mod] of Object.entries(metaModules)) {
  if (!file.endsWith("/index.json")) metaById.set((mod as ScriptMeta).id, mod as ScriptMeta)
}
const order = metaModules["../content/scripts/index.json"] as string[]

export const scripts: ScriptMeta[] = order.map((id) => {
  const meta = metaById.get(id)
  if (!meta) throw new Error(`scripts/index.json lists "${id}" but src/content/scripts/${id}.json is missing`)
  return meta
})

export async function loadScriptSource(script: ScriptMeta): Promise<string> {
  const load = sourceLoaders[`../content/code/${script.path}`]
  if (!load) throw new Error(`No source file found for ${script.path} (run "npm run sync")`)
  return (await load()).replace(/^\uFEFF/, "").replace(/\r\n/g, "\n").replace(/\n$/, "")
}

export interface PlacedNote {
  /** 1-based, inclusive. */
  start: number
  end: number
  text: string
}

/** Places each note on its anchor line; notes whose anchor no longer exists come back as `unmatched`. */
export function resolveNotes(source: string, notes: ScriptNote[]) {
  const lines = source.split("\n")
  const placed: PlacedNote[] = []
  const unmatched: ScriptNote[] = []
  for (const note of notes) {
    let seen = 0
    const index = lines.findIndex((l) => l.trim() === note.match && ++seen === (note.nth ?? 1))
    if (index === -1) {
      unmatched.push(note)
      continue
    }
    const start = index + 1
    placed.push({ start, end: Math.min(start + (note.span ?? 1) - 1, lines.length), text: note.text })
  }
  placed.sort((a, b) => a.start - b.start || a.end - b.end)
  return { placed, unmatched }
}
