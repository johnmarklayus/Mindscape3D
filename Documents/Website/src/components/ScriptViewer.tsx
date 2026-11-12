import { Suspense, lazy, useEffect, useMemo, useRef, useState } from "react"
import { FileCode2 } from "lucide-react"
import { type ScriptMeta, loadScriptSource, resolveNotes, scripts } from "@/data/scripts"
import { cn } from "@/lib/utils"
import { Badge } from "@/components/ui/badge"
import { H3, P, SectionTitle } from "@/components/Prose"
import { useLanguage, useUiCopy } from "@/lib/language"
import { localizeText } from "@/lib/localize"

// Monaco is big, so it only loads once a script is opened.
const CodeViewer = lazy(() => import("@/components/CodeViewer").then((m) => ({ default: m.CodeViewer })))

/** Code in the middle, the explanation of whichever line you're on in the panel to its right. */
export function ScriptView({ script }: { script: ScriptMeta }) {
  const [loaded, setLoaded] = useState<{ id: string; source: string } | { id: string; error: string } | null>(null)
  const [activeIndex, setActiveIndex] = useState<number | null>(null)
  const [revealSeq, setRevealSeq] = useState(0)
  const cardRefs = useRef<(HTMLButtonElement | null)[]>([])
  const { language } = useLanguage()
  const copy = useUiCopy()

  useEffect(() => {
    let cancelled = false
    loadScriptSource(script).then(
      (source) => !cancelled && setLoaded({ id: script.id, source }),
      (e: Error) => !cancelled && setLoaded({ id: script.id, error: e.message }),
    )
    return () => {
      cancelled = true
    }
  }, [script])

  const current = loaded?.id === script.id ? loaded : null
  const source = current && "source" in current ? current.source : null
  const { placed, unmatched } = useMemo(
    () => (source === null ? { placed: [], unmatched: [] } : resolveNotes(source, script.notes)),
    [source, script.notes],
  )

  useEffect(() => {
    if (import.meta.env.DEV && unmatched.length) {
      console.warn(`${script.path}: ${unmatched.length} note(s) no longer match a line`, unmatched)
    }
  }, [unmatched, script.path])

  const select = (index: number | null) => {
    setActiveIndex(index)
    if (index !== null) cardRefs.current[index]?.scrollIntoView({ block: "nearest", behavior: "smooth" })
  }

  return (
    <div className="flex flex-1 min-h-0 flex-col lg:flex-row">
      <div className="flex-1 min-w-0 min-h-[50vh] lg:min-h-0 border-b lg:border-b-0 lg:border-r border-border bg-white dark:bg-[#1e1e1e]">
        {current && "error" in current && <p className="p-4 text-sm text-red-700 dark:text-red-400">{current.error}</p>}
        {source !== null && (
          <Suspense fallback={<p className="p-4 text-sm text-muted-foreground">{copy.loadingEditor}</p>}>
            <CodeViewer
              key={script.id}
              source={source}
              notes={placed}
              activeIndex={activeIndex}
              revealSeq={revealSeq}
              onSelectNote={select}
            />
          </Suspense>
        )}
        {!current && <p className="p-4 text-sm text-muted-foreground">{copy.loading}</p>}
      </div>

      <aside className="lg:w-[380px] shrink-0 overflow-y-auto p-4 lg:max-h-none max-h-[45vh]">
        <div className="flex items-center gap-2">
          <FileCode2 className="size-4 text-sky-700 dark:text-sky-400" />
          <span className="font-mono font-semibold">{script.title}</span>
          <Badge variant="script">{script.notes.length} {copy.notes}</Badge>
        </div>
        <div className="text-xs text-muted-foreground font-mono mt-0.5">{script.path}</div>
        <p className="text-sm text-muted-foreground mt-2 leading-relaxed">{localizeText(script.summary, language)}</p>

        <H3>{copy.explanations}</H3>
        {source !== null && placed.length === 0 && (
          <p className="text-sm text-muted-foreground">{copy.noNotes}</p>
        )}
        <p className="text-xs text-muted-foreground mb-2">
          {copy.noteHelp}
        </p>
        <ol className="space-y-2">
          {placed.map((n, i) => (
            <li key={`${n.start}-${i}`}>
              <button
                ref={(el) => {
                  cardRefs.current[i] = el
                }}
                onClick={() => {
                  setActiveIndex(i)
                  setRevealSeq((s) => s + 1)
                }}
                className={cn(
                  "w-full text-left rounded-md border p-2.5 text-[13px] leading-snug transition-colors",
                  i === activeIndex
                    ? "border-emerald-500/60 bg-emerald-500/10"
                    : "border-border hover:bg-foreground/[0.03]",
                )}
              >
                <span className="block font-mono text-[11px] text-emerald-700 dark:text-emerald-400 mb-1">
                  {n.start === n.end ? `${copy.line} ${n.start}` : `${copy.lines} ${n.start}–${n.end}`}
                </span>
                {localizeText(n.text, language)}
              </button>
            </li>
          ))}
        </ol>
        {unmatched.length > 0 && (
          <p className="mt-3 text-xs text-amber-700 dark:text-amber-400">
            {unmatched.length} {copy.staleNotes}
          </p>
        )}
      </aside>
    </div>
  )
}

export function ScriptsOverview() {
  const { language } = useLanguage()
  const copy = useUiCopy()
  return (
    <div className="px-5 py-10 md:px-16 md:py-14 max-w-4xl">
      <SectionTitle>{copy.scriptsTitle}</SectionTitle>
      <P>{copy.scriptsIntro}</P>
      <div className="grid gap-3 sm:grid-cols-2 mt-6">
        {scripts.map((s) => (
          <a key={s.id} href={`#${s.id}`} className="rounded-lg border border-border bg-card p-3.5 hover:bg-foreground/[0.03]">
            <div className="font-mono font-semibold text-[14px] text-sky-700 dark:text-sky-400">{s.title}</div>
            <div className="text-[12.5px] text-muted-foreground mt-1 line-clamp-2">
              {localizeText(s.summary, language)}
            </div>
          </a>
        ))}
      </div>
    </div>
  )
}
