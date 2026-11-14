import { Children, isValidElement, useEffect, useMemo, useRef, useState, type ReactNode } from "react"
import ReactMarkdown, { type Components } from "react-markdown"
import remarkGfm from "remark-gfm"
import { ArrowLeft, ArrowRight, ChevronRight, Gamepad2, Menu } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet"
import { components } from "@/components/Markdown"
import { H2 } from "@/components/Prose"
import { ThemeToggle } from "@/components/ThemeToggle"
import { LanguageToggle } from "@/components/LanguageToggle"
import { onboardingGroups, onboardingTopics, type OnboardingTopic } from "@/data/onboarding"
import { useLanguage, useUiCopy } from "@/lib/language"
import { localizeMarkdown, localizeNavigation } from "@/lib/localize"
import { cn } from "@/lib/utils"

// Links made before the onboarding was split into topics.
const LEGACY: Record<string, string> = {
  "make-a-scene-an-episode-and-a-chapter": "create-episode",
  "build-scenes-episodes-and-chapters": "scenes",
}

function slug(text: string) {
  return text.replace(/^\d+\.\s*/, "").toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "")
}

function textOf(node: ReactNode): string {
  return Children.toArray(node)
    .map((child) => (typeof child === "string" || typeof child === "number" ? String(child) : isValidElement<{ children?: ReactNode }>(child) ? textOf(child.props.children) : ""))
    .join("")
}

function useTopic(): OnboardingTopic {
  const read = () => {
    const hash = decodeURIComponent(window.location.hash.slice(1))
    const id = LEGACY[hash] ?? hash
    return onboardingTopics.find((t) => t.id === id) ?? onboardingTopics[0]
  }
  const [topic, setTopic] = useState(read)
  useEffect(() => {
    const onChange = () => setTopic(read())
    window.addEventListener("hashchange", onChange)
    return () => window.removeEventListener("hashchange", onChange)
  }, [])
  return topic
}

/** The sidebar: one accordion section per group; the section of the open topic starts expanded. */
function OnboardingNav({ active, onNavigate }: { active: OnboardingTopic; onNavigate?: () => void }) {
  const { language } = useLanguage()
  const copy = useUiCopy()
  const [query, setQuery] = useState("")
  const [open, setOpen] = useState<Set<string>>(() => new Set([active.group]))
  useEffect(() => setOpen((o) => (o.has(active.group) ? o : new Set(o).add(active.group))), [active.group])
  const q = query.trim().toLowerCase()
  const groups = useMemo(
    () =>
      onboardingGroups
        .map((g) => ({
          ...g,
          label: localizeNavigation(g.title, language),
          topics: g.topics.filter((t) => !q || localizeNavigation(t.nav, language).toLowerCase().includes(q) || g.title.toLowerCase().includes(q)),
        }))
        .filter((g) => g.topics.length > 0),
    [language, q],
  )
  const toggle = (title: string) =>
    setOpen((o) => {
      const next = new Set(o)
      if (next.has(title)) next.delete(title)
      else next.add(title)
      return next
    })

  return (
    <div className="flex h-full flex-col p-4">
      <div className="mb-1">
        <div className="text-lg font-extrabold tracking-tight">{copy.onboarding}</div>
        <div className="text-[12.5px] text-muted-foreground mb-4">{copy.onboardingTitle}</div>
      </div>
      <Input placeholder={copy.filterOnboarding} value={query} onChange={(e) => setQuery(e.target.value)} className="mb-3" />
      <nav className="flex-1 overflow-y-auto -mx-1 px-1 space-y-0.5">
        {groups.map((group) => {
          const expanded = q !== "" || open.has(group.title)
          const holdsActive = group.topics.some((t) => t.id === active.id)
          return (
            <div key={group.title}>
              <button
                type="button"
                onClick={() => toggle(group.title)}
                aria-expanded={expanded}
                className={cn(
                  "flex w-full items-center gap-1.5 rounded-md px-2 py-2 text-left text-[13.5px] font-semibold hover:bg-secondary",
                  holdsActive ? "text-foreground" : "text-muted-foreground",
                )}
              >
                <ChevronRight className={cn("size-4 shrink-0 transition-transform duration-150", expanded && "rotate-90")} />
                <span className="flex-1 truncate">{group.label}</span>
                <span className="text-[11px] font-normal text-muted-foreground">{group.topics.length}</span>
              </button>
              {expanded && (
                <div className="ml-[17px] mb-1 border-l border-border pl-2">
                  {group.topics.map((t) => (
                    <a
                      key={t.id}
                      href={`#${t.id}`}
                      onClick={onNavigate}
                      className={cn(
                        "block rounded-md px-2.5 py-1.5 text-[13.5px] text-muted-foreground hover:bg-secondary hover:text-foreground whitespace-nowrap overflow-hidden text-ellipsis",
                        t.id === active.id && "bg-primary/10 text-primary font-semibold",
                      )}
                    >
                      {localizeNavigation(t.nav, language)}
                    </a>
                  ))}
                </div>
              )}
            </div>
          )
        })}
      </nav>
    </div>
  )
}

/**
 * /onboarding: the whole journey of the game, from an empty computer to a published release, as short topics
 * (src/content/onboarding/*.md) grouped in an accordion sidebar. #topic-id picks the topic; Previous / Next walk them in order.
 */
export function OnboardingPage() {
  const { language } = useLanguage()
  const copy = useUiCopy()
  const topic = useTopic()
  const [mobileOpen, setMobileOpen] = useState(false)
  const mainRef = useRef<HTMLDivElement>(null)
  const index = onboardingTopics.indexOf(topic)
  const previous = onboardingTopics[index - 1]
  const next = onboardingTopics[index + 1]
  const body = localizeMarkdown(topic.body, language)
  const headings = useMemo(
    () => [...body.matchAll(/^## (.+)$/gm)].map((m) => ({ id: slug(m[1].replace(/`/g, "")), label: m[1].replace(/`/g, "") })),
    [body],
  )
  const [current, setCurrent] = useState<string | undefined>()

  useEffect(() => {
    document.title = `${localizeNavigation(topic.nav, language)} · ${copy.onboarding} — ${copy.docsTitle}`
    mainRef.current?.scrollTo({ top: 0 })
    setCurrent(headings[0]?.id)
  }, [topic, language, copy.onboarding, copy.docsTitle, headings])

  // Highlights the part of the topic being read: the last heading scrolled past (long code blocks included).
  useEffect(() => {
    const root = mainRef.current
    if (!root) return
    const update = () => {
      const top = root.getBoundingClientRect().top + 120
      let id = headings[0]?.id
      for (const h of headings) {
        const el = document.getElementById(h.id)
        if (el && el.getBoundingClientRect().top <= top) id = h.id
      }
      setCurrent(id)
    }
    update()
    root.addEventListener("scroll", update, { passive: true })
    return () => root.removeEventListener("scroll", update)
  }, [headings])

  const pageComponents: Components = {
    ...components,
    h2: ({ children }) => <H2 id={slug(textOf(children))}>{children}</H2>,
  }

  return (
    <div className="h-screen flex flex-col md:flex-row bg-background text-foreground overflow-hidden">
      <aside className="hidden md:block w-72 shrink-0 border-r border-border bg-sidebar">
        <OnboardingNav active={topic} />
      </aside>

      <div className="flex-1 min-w-0 min-h-0 flex flex-col">
        <header className="flex items-center gap-2 h-12 px-3 border-b border-border bg-sidebar shrink-0">
          <Sheet open={mobileOpen} onOpenChange={setMobileOpen}>
            <SheetTrigger asChild>
              <Button variant="outline" size="icon" className="md:hidden" aria-label={copy.openNavigation}>
                <Menu />
              </Button>
            </SheetTrigger>
            <SheetContent side="left" className="w-80">
              <OnboardingNav active={topic} onNavigate={() => setMobileOpen(false)} />
            </SheetContent>
          </Sheet>
          <Button asChild variant="ghost" size="sm" className="shrink-0">
            <a href="/">
              <ArrowLeft />
              <span className="max-sm:hidden">{copy.backToDocs}</span>
            </a>
          </Button>
          <span className="min-w-0 flex-1 text-sm truncate">
            <span className="text-muted-foreground">{localizeNavigation(topic.group, language)} › </span>
            <span className="font-semibold">{localizeNavigation(topic.nav, language)}</span>
          </span>
          <LanguageToggle />
          <ThemeToggle />
          <Button asChild size="sm" className="shrink-0">
            <a href="/#play-game">
              <Gamepad2 />
              <span className="max-lg:hidden">{copy.playGame}</span>
            </a>
          </Button>
        </header>

        <div ref={mainRef} className="flex-1 min-h-0 overflow-y-auto">
          <div className="flex gap-10 px-5 md:px-12">
            <article className="min-w-0 flex-1 max-w-3xl py-10 md:py-14 [&>h1+p]:text-muted-foreground [&>h1+p]:mb-6">
              <ReactMarkdown remarkPlugins={[remarkGfm]} components={pageComponents}>
                {body}
              </ReactMarkdown>

              <div className="mt-14 grid grid-cols-2 gap-3 border-t border-border pt-6">
                {previous ? (
                  <a href={`#${previous.id}`} className="group rounded-lg border border-border p-3 hover:bg-secondary">
                    <span className="flex items-center gap-1 text-xs text-muted-foreground"><ArrowLeft className="size-3.5" /> {copy.previous}</span>
                    <span className="mt-1 block text-sm font-semibold">{localizeNavigation(previous.nav, language)}</span>
                  </a>
                ) : <span />}
                {next && (
                  <a href={`#${next.id}`} className="group rounded-lg border border-border p-3 text-right hover:bg-secondary">
                    <span className="flex items-center justify-end gap-1 text-xs text-muted-foreground">{copy.next} <ArrowRight className="size-3.5" /></span>
                    <span className="mt-1 block text-sm font-semibold">{localizeNavigation(next.nav, language)}</span>
                  </a>
                )}
              </div>
            </article>

            {headings.length > 1 && (
              <nav aria-label={copy.onThisPage} className="hidden xl:block w-56 shrink-0">
                <div className="sticky top-0 py-14">
                  <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-muted-foreground">{copy.onThisPage}</p>
                  <ol className="space-y-1.5 border-l border-border text-sm">
                    {headings.map((h) => (
                      <li key={h.id}>
                        <button
                          type="button"
                          // Scrolls without touching the #topic in the address.
                          onClick={() => document.getElementById(h.id)?.scrollIntoView({ behavior: "smooth", block: "start" })}
                          className={cn(
                            "-ml-px block w-full border-l pl-3 text-left leading-snug hover:text-foreground",
                            current === h.id ? "border-foreground font-medium text-foreground" : "border-transparent text-muted-foreground",
                          )}
                        >
                          {h.label}
                        </button>
                      </li>
                    ))}
                  </ol>
                </div>
              </nav>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
