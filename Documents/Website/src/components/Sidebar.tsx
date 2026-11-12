import { useMemo, useState } from "react"
import { cn } from "@/lib/utils"
import { Input } from "@/components/ui/input"
import { docNavGroups, type NavGroup } from "@/data/docs"
import { scripts } from "@/data/scripts"
import { useLanguage, useUiCopy } from "@/lib/language"
import { localizeNavigation } from "@/lib/localize"

export function SidebarContent({ active, onNavigate }: { active: string; onNavigate?: () => void }) {
  const [query, setQuery] = useState("")
  const { language } = useLanguage()
  const copy = useUiCopy()
  const q = query.trim().toLowerCase()
  const allGroups: NavGroup[] = useMemo(
    () => [
      ...docNavGroups.map((group) => ({
        title: localizeNavigation(group.title, language),
        items: group.items.map((item) => ({ ...item, label: localizeNavigation(item.label, language) })),
      })),
      {
        title: copy.scriptsGroup,
        items: [
          { href: "#scripts", label: copy.overview },
          ...scripts.map((s) => ({ href: `#${s.id}`, label: localizeNavigation(s.title, language) })),
        ],
      },
    ],
    [copy.overview, copy.scriptsGroup, language],
  )
  const groups = useMemo(
    () =>
      allGroups
        .map((g) => ({ ...g, items: q ? g.items.filter((i) => i.label.toLowerCase().includes(q)) : g.items }))
        .filter((g) => g.items.length > 0),
    [allGroups, q],
  )

  return (
    <div className="flex h-full flex-col p-4">
      <div className="mb-1">
        <div className="text-lg font-extrabold tracking-tight">Mindscape 3D</div>
        <div className="text-[12.5px] text-muted-foreground mb-4">{copy.projectDocs}</div>
      </div>
      <Input
        placeholder={copy.filterTopics}
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        className="mb-3"
      />
      <nav className="flex-1 overflow-y-auto -mx-1 px-1 space-y-1">
        {groups.map((group) => (
          <div key={group.title} className="mb-1">
            <div className="uppercase text-[11px] tracking-wide text-muted-foreground px-2 pt-2.5 pb-1.5">
              {group.title}
            </div>
            {group.items.map((item) => (
              <a
                key={item.href}
                href={item.href}
                onClick={onNavigate}
                className={cn(
                  "block rounded-md px-2.5 py-1.5 text-[13.5px] text-muted-foreground hover:bg-secondary hover:text-foreground whitespace-nowrap overflow-hidden text-ellipsis",
                  active === item.href.slice(1) && "bg-primary/10 text-primary font-semibold",
                )}
              >
                {item.label}
              </a>
            ))}
          </div>
        ))}
      </nav>
    </div>
  )
}
