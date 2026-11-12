import { Languages } from "lucide-react"
import { cn } from "@/lib/utils"
import { useLanguage } from "@/lib/language"

export function LanguageToggle() {
  const { language, setLanguage } = useLanguage()

  return (
    <div
      className="inline-flex h-9 shrink-0 items-center rounded-md border border-border bg-background p-0.5"
      role="group"
      aria-label="Documentation language / Wika ng dokumentasyon"
      title="Documentation language / Wika ng dokumentasyon"
    >
      <Languages className="mx-1.5 size-3.5 text-muted-foreground max-sm:hidden" aria-hidden="true" />
      {(["en", "fil"] as const).map((option) => (
        <button
          key={option}
          type="button"
          aria-pressed={language === option}
          aria-label={option === "en" ? "Read in English" : "Basahin sa Filipino (Taglish)"}
          onClick={() => setLanguage(option)}
          className={cn(
            "h-7 min-w-9 rounded px-2 text-[11px] font-bold tracking-wide transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
            language === option
              ? "bg-primary text-primary-foreground"
              : "text-muted-foreground hover:bg-secondary hover:text-foreground",
          )}
        >
          {option === "en" ? "EN" : "FIL"}
        </button>
      ))}
    </div>
  )
}
