import type { ReactNode } from "react"
import { cn } from "@/lib/utils"

export function SectionTitle({ children }: { children: ReactNode }) {
  return <h1 className="text-3xl font-bold tracking-tight mb-1.5">{children}</h1>
}

export function Lede({ children }: { children: ReactNode }) {
  return <p className="text-muted-foreground text-[15px] mb-6 leading-relaxed">{children}</p>
}

export function H2({ children }: { children: ReactNode }) {
  return (
    <h2 className="text-xl font-semibold mt-9 mb-2.5 pt-2 border-t border-border first:border-t-0 first:pt-0 first:mt-0">
      {children}
    </h2>
  )
}

export function H3({ children }: { children: ReactNode }) {
  return <h3 className="text-base font-semibold mt-6 mb-2 text-sky-700 dark:text-sky-400">{children}</h3>
}

export function P({ children }: { children: ReactNode }) {
  return <p className="my-2.5 leading-relaxed text-[15px]">{children}</p>
}

export function List({ children, ordered }: { children: ReactNode; ordered?: boolean }) {
  const Tag = ordered ? "ol" : "ul"
  return <Tag className={cn("my-2.5 pl-5 space-y-1.5 text-[15px]", ordered ? "list-decimal" : "list-disc")}>{children}</Tag>
}

export function Callout({
  variant = "tip",
  label,
  children,
}: {
  variant?: "tip" | "warn"
  label: string
  children: ReactNode
}) {
  return (
    <div
      className={cn(
        "rounded-lg border p-3.5 my-3.5 text-sm",
        variant === "tip" && "border-emerald-500/40 bg-emerald-500/[0.06]",
        variant === "warn" && "border-amber-500/40 bg-amber-500/[0.06]",
      )}
    >
      <span
        className={cn(
          "block font-bold uppercase text-[11px] tracking-wide mb-1",
          variant === "tip" && "text-emerald-700 dark:text-emerald-400",
          variant === "warn" && "text-amber-700 dark:text-amber-400",
        )}
      >
        {label}
      </span>
      {children}
    </div>
  )
}

export function Card({ children }: { children: ReactNode }) {
  return <div className="rounded-lg border border-border bg-card p-4 my-3.5">{children}</div>
}

export function CardTitle({ children }: { children: ReactNode }) {
  return <div className="font-bold mb-1.5 flex items-center gap-2">{children}</div>
}

export function Steps({ children }: { children: ReactNode }) {
  return <ol className="list-none pl-0 [counter-reset:step]">{children}</ol>
}

export function Step({ children }: { children: ReactNode }) {
  return (
    <li className="relative py-2.5 pl-10 ml-3.5 border-l-2 border-border last:border-transparent [counter-increment:step]">
      <span className="absolute -left-[15px] top-2 w-7 h-7 rounded-full bg-secondary border border-border text-primary font-bold text-[13px] flex items-center justify-center before:content-[counter(step)]" />
      <div className="text-[15px] leading-relaxed">{children}</div>
    </li>
  )
}

export function FileTree({ children }: { children: ReactNode }) {
  return (
    <pre className="font-mono text-[13px] bg-code border border-border rounded-lg p-4 overflow-x-auto text-foreground whitespace-pre my-3.5">
      {children}
    </pre>
  )
}

export function Table({ children }: { children: ReactNode }) {
  return (
    <div className="my-3.5 overflow-x-auto">
      <table className="w-full border-collapse text-[13.5px]">{children}</table>
    </div>
  )
}

export function Th({ children }: { children: ReactNode }) {
  return (
    <th className="text-left px-2.5 py-2 border-b border-border text-muted-foreground font-semibold text-[12px] uppercase tracking-wide">
      {children}
    </th>
  )
}

export function Td({ children }: { children: ReactNode }) {
  return <td className="text-left px-2.5 py-2 border-b border-border align-top">{children}</td>
}

export function Tr({ children }: { children: ReactNode }) {
  return <tr className="hover:bg-foreground/[0.02]">{children}</tr>
}
