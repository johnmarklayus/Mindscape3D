import { cn } from "@/lib/utils"
import { useEffect, useRef, useState } from "react"
import { Download, Gamepad2, Menu, PanelLeftClose, PanelLeftOpen } from "lucide-react"
import { SidebarContent } from "@/components/Sidebar"
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet"
import { Button } from "@/components/ui/button"
import { DocSectionView } from "@/components/Markdown"
import { PlayGame } from "@/components/PlayGame"
import { ThemeToggle } from "@/components/ThemeToggle"
import { LanguageToggle } from "@/components/LanguageToggle"
import { ScriptView, ScriptsOverview } from "@/components/ScriptViewer"
import { docSections } from "@/data/docs"
import { formatReleaseDate, latestBuild } from "@/data/build"
import { scripts } from "@/data/scripts"
import { useLanguage, useUiCopy } from "@/lib/language"
import { localizeNavigation } from "@/lib/localize"

function useHash() {
  const read = () => decodeURIComponent(window.location.hash.slice(1))
  const [hash, setHash] = useState(read)
  useEffect(() => {
    const onChange = () => setHash(read())
    window.addEventListener("hashchange", onChange)
    return () => window.removeEventListener("hashchange", onChange)
  }, [])
  return hash
}

function App() {
  const [mobileOpen, setMobileOpen] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const hash = useHash()
  const proseRef = useRef<HTMLDivElement>(null)
  const { language } = useLanguage()
  const copy = useUiCopy()

  const playing = hash === "play-game"
  const script = scripts.find((s) => s.id === hash)
  const section = docSections.find((s) => s.id === hash) ?? (script || playing || hash === "scripts" ? undefined : docSections[0])
  const active = playing ? "play-game" : (script?.id ?? section?.id ?? "scripts")
  const title = playing
    ? copy.playGameTitle
    : localizeNavigation(script?.title ?? section?.nav ?? copy.scripts, language)

  useEffect(() => {
    proseRef.current?.scrollTo({ top: 0 })
    document.title = `${title} — ${copy.docsTitle}`
  }, [active, copy.docsTitle, title])

  return (
    <div className="h-screen flex flex-col md:flex-row bg-background text-foreground overflow-hidden">
      {/* Desktop sidebar (collapsible) */}
      <aside
        className={cn(
          "hidden md:block shrink-0 border-r border-border bg-sidebar overflow-hidden transition-[width] duration-200",
          sidebarOpen ? "w-72" : "w-0 border-r-0",
        )}
      >
        <div className="w-72 h-full">
          <SidebarContent active={active} />
        </div>
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
              <SidebarContent active={active} onNavigate={() => setMobileOpen(false)} />
            </SheetContent>
          </Sheet>
          <Button
            variant="ghost"
            size="icon"
            className="hidden md:inline-flex"
            aria-label={sidebarOpen ? copy.collapseNavigation : copy.expandNavigation}
            onClick={() => setSidebarOpen((o) => !o)}
          >
            {sidebarOpen ? <PanelLeftClose /> : <PanelLeftOpen />}
          </Button>
          <span className="min-w-0 flex-1 font-semibold text-sm truncate">{title}</span>
          <span className="ml-auto hidden lg:block text-xs text-muted-foreground text-right leading-tight shrink-0">
            v{latestBuild.version}
            <br />
            {copy.released} {formatReleaseDate(latestBuild.releaseDate, language === "fil" ? "fil-PH" : "en")}
          </span>
          <LanguageToggle />
          <ThemeToggle />
          {latestBuild.apkUrl && (
            <Button asChild variant="outline" size="sm" className="shrink-0 max-sm:ml-auto">
              <a
                href={latestBuild.apkUrl}
                download
                title={`Version ${latestBuild.version} · ${formatReleaseDate(latestBuild.releaseDate, language === "fil" ? "fil-PH" : "en")} · ${latestBuild.apkSize}`}
              >
                <Download />
                <span className="max-xl:hidden">{copy.downloadApk}</span>
              </a>
            </Button>
          )}
          <Button asChild size="sm" className="shrink-0">
            <a href="#play-game">
              <Gamepad2 />
              <span className="max-lg:hidden">{copy.playGame}</span>
            </a>
          </Button>
        </header>

        {playing ? (
          <PlayGame />
        ) : script ? (
          <ScriptView script={script} />
        ) : (
          <div ref={proseRef} className="flex-1 min-h-0 overflow-y-auto">
            {section ? (
              <div className="px-5 py-10 md:px-16 md:py-14 max-w-4xl">
                <DocSectionView section={section} />
              </div>
            ) : (
              <ScriptsOverview />
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default App
