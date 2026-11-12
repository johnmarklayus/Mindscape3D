"use client"

import { Box, Button, CloseButton, Dialog, HStack, Portal, Text } from "@chakra-ui/react"
import { useCallback, useEffect, useRef, useState } from "react"
import { legal, PrivacyContent, TermsContent } from "./legal-content"

// The Privacy Policy and Terms open in a modal on any page. A link only needs a hash:
//   #privacy, #terms             open the document at the top
//   #privacy-cookies, #terms-law  open it at that section
// so the documents still have shareable addresses (https://your-domain/#privacy). Closing the modal removes the hash.

type Doc = keyof typeof legal

function parse(hash: string): { doc: Doc; section?: string } | null {
  const m = /^#(privacy|terms)(?:-([\w-]+))?$/.exec(hash)
  return m ? { doc: m[1] as Doc, section: m[2] ? `${m[1]}-${m[2]}` : undefined } : null
}

export function LegalModal() {
  const [doc, setDoc] = useState<Doc | null>(null)
  const [section, setSection] = useState<string | undefined>()
  const bodyRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const sync = () => {
      const target = parse(window.location.hash)
      if (target) {
        setDoc(target.doc)
        setSection(target.section)
        return
      }
      setDoc((open) => {
        // Another in-page link was followed from inside the modal (e.g. "contact form"): close and go there.
        if (open && window.location.hash) {
          const id = window.location.hash.slice(1)
          setTimeout(() => document.getElementById(id)?.scrollIntoView({ behavior: "smooth" }), 50)
        }
        return null
      })
    }
    sync()
    window.addEventListener("hashchange", sync)
    return () => window.removeEventListener("hashchange", sync)
  }, [])

  // Scroll the modal to the requested section (or the top when switching documents).
  useEffect(() => {
    if (!doc) return
    const t = setTimeout(() => {
      const el = section ? document.getElementById(section) : null
      if (el) el.scrollIntoView({ block: "start" })
      else bodyRef.current?.scrollTo({ top: 0 })
    }, 60)
    return () => clearTimeout(t)
  }, [doc, section])

  const close = useCallback(() => {
    setDoc(null)
    if (parse(window.location.hash)) history.replaceState(null, "", window.location.pathname + window.location.search)
  }, [])

  const show = (d: Doc) => {
    window.location.hash = d
  }

  return (
    <Dialog.Root open={doc !== null} onOpenChange={(e) => !e.open && close()} size="xl" scrollBehavior="inside" placement="center">
      <Portal>
        <Dialog.Backdrop />
        <Dialog.Positioner>
          <Dialog.Content bg="bg.panel" borderWidth="1px" borderColor="brass.border" mx="3" maxH="calc(100dvh - 2rem)">
            <Dialog.Header flexDirection="column" alignItems="flex-start" gap="3" borderBottomWidth="1px" borderColor="border" pb="4">
              <HStack gap="1" bg="bg.muted" p="1" rounded="md" role="tablist" aria-label="Legal documents">
                {(Object.keys(legal) as Doc[]).map((d) => (
                  <Button
                    key={d}
                    size="xs"
                    role="tab"
                    aria-selected={doc === d}
                    variant={doc === d ? "solid" : "ghost"}
                    colorPalette="brass"
                    onClick={() => show(d)}
                  >
                    {legal[d].title}
                  </Button>
                ))}
              </HStack>
              <Box>
                <Dialog.Title fontFamily="heading" fontSize={{ base: "2xl", md: "3xl" }} fontWeight="semibold" color="fg">
                  {doc ? legal[doc].title : ""}
                </Dialog.Title>
                <Text fontSize="sm" color="fg.subtle">
                  {doc ? `Last updated ${legal[doc].updated}` : ""}
                </Text>
              </Box>
            </Dialog.Header>
            <Dialog.Body
              ref={bodyRef}
              px={{ base: "4", md: "6" }}
              py="5"
              lineHeight="1.75"
              css={{
                "& .lead": { fontSize: "lg", color: "fg", mb: "6" },
                "& h2": { fontFamily: "heading", fontSize: "1.45rem", fontWeight: 600, mt: "8", mb: "3", color: "fg", scrollMarginTop: "8px" },
                "& h3": { fontWeight: 700, mt: "5", mb: "2", scrollMarginTop: "8px" },
                "& p": { mb: "4", color: "fg.muted" },
                "& ul": { mb: "4", ps: "6", listStyleType: "disc", color: "fg.muted" },
                "& li": { mb: "1.5" },
                "& a": { color: "brass.fg", textDecoration: "underline" },
                "& strong": { color: "fg" },
              }}
            >
              {doc === "privacy" && <PrivacyContent />}
              {doc === "terms" && <TermsContent />}
            </Dialog.Body>
            <Dialog.Footer borderTopWidth="1px" borderColor="border" pt="4">
              <Button colorPalette="brass" onClick={close}>
                Close
              </Button>
            </Dialog.Footer>
            <Dialog.CloseTrigger asChild>
              <CloseButton size="sm" />
            </Dialog.CloseTrigger>
          </Dialog.Content>
        </Dialog.Positioner>
      </Portal>
    </Dialog.Root>
  )
}
