import { useEffect, useRef, useState } from "react"
import Editor, { loader, type OnMount } from "@monaco-editor/react"
import * as monaco from "monaco-editor/editor/editor.api"
import "monaco-editor/languages/definitions/csharp/register"
import EditorWorker from "monaco-editor/editor/editor.worker?worker"
import type { PlacedNote } from "@/data/scripts"
import { useTheme } from "@/lib/theme"

// Bundle Monaco (only the editor core + C# highlighting) instead of fetching it from a CDN.
self.MonacoEnvironment = { getWorker: () => new EditorWorker() }
loader.config({ monaco })

type Editor = monaco.editor.IStandaloneCodeEditor

/** A read-only Monaco editor. Annotated lines are tinted; clicking one reports its note. */
export function CodeViewer({
  source,
  notes,
  activeIndex,
  revealSeq,
  onSelectNote,
}: {
  source: string
  notes: PlacedNote[]
  activeIndex: number | null
  /** Bumped when the explanation panel asks the editor to scroll to the active note. */
  revealSeq: number
  onSelectNote: (index: number | null) => void
}) {
  const { theme } = useTheme()
  const editorRef = useRef<Editor | null>(null)
  const decorationsRef = useRef<monaco.editor.IEditorDecorationsCollection | null>(null)
  const [mounted, setMounted] = useState(false)
  const notesRef = useRef(notes)
  const onSelectRef = useRef(onSelectNote)
  useEffect(() => {
    notesRef.current = notes
    onSelectRef.current = onSelectNote
  })

  const handleMount: OnMount = (editor) => {
    editorRef.current = editor
    decorationsRef.current = editor.createDecorationsCollection()
    setMounted(true)
    editor.onMouseDown((e) => {
      const line = e.target.position?.lineNumber
      if (!line) return
      // Prefer the tightest note covering the clicked line.
      let best: number | null = null
      notesRef.current.forEach((n, i) => {
        if (line >= n.start && line <= n.end) {
          const b = best === null ? null : notesRef.current[best]
          if (!b || n.end - n.start < b.end - b.start) best = i
        }
      })
      onSelectRef.current(best)
    })
  }

  useEffect(() => {
    decorationsRef.current?.set(
      notes.map((n, i) => ({
        range: new monaco.Range(n.start, 1, n.end, 1),
        options: {
          isWholeLine: true,
          className: i === activeIndex ? "note-line note-line-active" : "note-line",
          glyphMarginClassName: "note-glyph",
        },
      })),
    )
  }, [mounted, notes, activeIndex, source])

  useEffect(() => {
    const note = activeIndex === null ? null : notes[activeIndex]
    if (note) editorRef.current?.revealLinesInCenterIfOutsideViewport(note.start, note.end)
    // Only scroll when the panel asks, not while the user is clicking inside the editor.
  }, [revealSeq])

  return (
    <Editor
      height="100%"
      language="csharp"
      theme={theme === "dark" ? "vs-dark" : "vs"}
      value={source}
      onMount={handleMount}
      loading={<div className="p-4 text-sm text-muted-foreground">Loading editor…</div>}
      options={{
        readOnly: true,
        domReadOnly: true,
        minimap: { enabled: false },
        glyphMargin: true,
        scrollBeyondLastLine: false,
        renderLineHighlight: "none",
        fontSize: 13,
        automaticLayout: true,
        padding: { top: 12, bottom: 12 },
      }}
    />
  )
}
