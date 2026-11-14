import { Children, isValidElement, type ReactNode } from "react"
import ReactMarkdown, { type Components } from "react-markdown"
import remarkGfm from "remark-gfm"
import { Badge } from "@/components/ui/badge"
import { Callout, Card, CardTitle, FileTree, H2, H3, List, P, SectionTitle, Step, Steps, Table, Td, Th, Tr } from "@/components/Prose"
import type { DocSection } from "@/data/docs"
import { useLanguage, useUiCopy } from "@/lib/language"
import { localizeMarkdown } from "@/lib/localize"

/** A blockquote whose first line is `[!TIP] Label`, `[!WARN] Label`, or `[!MENU] Label` becomes a callout/card. */
const ALERT = /^\[!(TIP|WARN|MENU)\]\s*(.*)$/

function Blockquote({ children }: { children?: ReactNode }) {
  const copy = useUiCopy()
  const blocks = Children.toArray(children).filter(isValidElement<{ children?: ReactNode }>)
  const first = Children.toArray(blocks[0]?.props.children)[0]
  const alert = typeof first === "string" ? ALERT.exec(first) : null
  if (!alert) {
    return <blockquote className="my-3.5 border-l-2 border-border pl-4 text-muted-foreground">{children}</blockquote>
  }
  const [, kind, label] = alert
  const body = blocks.slice(1)
  if (kind === "MENU") {
    return (
      <Card>
        <CardTitle>
          {label} <Badge variant="menu">{copy.menuItem}</Badge>
        </CardTitle>
        {body}
      </Card>
    )
  }
  return (
    <Callout variant={kind === "WARN" ? "warn" : "tip"} label={label}>
      {body}
    </Callout>
  )
}

function OrderedSteps({ children }: { children?: ReactNode }) {
  return (
    <Steps>
      {Children.toArray(children)
        .filter(isValidElement<{ children?: ReactNode }>)
        .map((li, i) => (
          <Step key={i}>{li.props.children}</Step>
        ))}
    </Steps>
  )
}

export const components: Components = {
  h1: ({ children }) => <SectionTitle>{children}</SectionTitle>,
  h2: ({ children }) => <H2>{children}</H2>,
  h3: ({ children }) => <H3>{children}</H3>,
  p: ({ children }) => <P>{children}</P>,
  ul: ({ children }) => <List>{children}</List>,
  ol: OrderedSteps,
  blockquote: Blockquote,
  pre: ({ children }) => (
    <FileTree>
      {(isValidElement<{ children?: ReactNode }>(children) ? children.props.children : children) as ReactNode}
    </FileTree>
  ),
  table: ({ children }) => <Table>{children}</Table>,
  tr: ({ children }) => <Tr>{children}</Tr>,
  th: ({ children }) => <Th>{children}</Th>,
  td: ({ children }) => <Td>{children}</Td>,
  a: ({ href, children }) => (
    <a href={href} className="text-sky-700 dark:text-sky-400 hover:underline">
      {children}
    </a>
  ),
}

export function DocSectionView({ section }: { section: DocSection }) {
  const { language } = useLanguage()
  return (
    <section
      id={section.id}
      // The paragraph right under the title is the section's lede.
      className="scroll-mt-6 mb-14 [&>h1+p]:text-muted-foreground [&>h1+p]:mb-6"
    >
      <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
        {localizeMarkdown(section.body, language)}
      </ReactMarkdown>
    </section>
  )
}
