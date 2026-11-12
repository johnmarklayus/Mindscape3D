"use client"

import { Box, Button, CloseButton, Dialog, Flex, HStack, Link, Portal, Stack, Switch, Text } from "@chakra-ui/react"
import { Analytics } from "@vercel/analytics/next"
import { usePathname } from "next/navigation"
import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from "react"

// Cookie consent. Strictly necessary storage (this choice) is always on; analytics
// (Vercel Web Analytics: anonymous, aggregated page views) only loads after the visitor allows it.
// The choice is kept for 180 days in localStorage and a first-party cookie, and can be changed from the footer.

export type Consent = { necessary: true; analytics: boolean; decidedAt: string; version: 1 }

const KEY = "mindscape-consent"
const MAX_AGE_DAYS = 180

type ConsentState = {
  consent: Consent | null
  ready: boolean
  save: (analytics: boolean) => void
  openSettings: () => void
}

const ConsentContext = createContext<ConsentState | null>(null)

export function useConsent() {
  const ctx = useContext(ConsentContext)
  if (!ctx) throw new Error("useConsent must be used inside ConsentProvider")
  return ctx
}

function readConsent(): Consent | null {
  try {
    const raw = window.localStorage.getItem(KEY)
    if (!raw) return null
    const parsed = JSON.parse(raw) as Consent
    const age = (Date.now() - new Date(parsed.decidedAt).getTime()) / 86400000
    return parsed.version === 1 && age < MAX_AGE_DAYS ? parsed : null
  } catch {
    return null
  }
}

export function ConsentProvider({ children }: { children: ReactNode }) {
  const [consent, setConsent] = useState<Consent | null>(null)
  const [ready, setReady] = useState(false)
  const [settingsOpen, setSettingsOpen] = useState(false)
  // The game page shows only the game: the banner waits for the next site page (analytics stay off until then).
  const onGamePage = usePathname() === "/play"

  useEffect(() => {
    setConsent(readConsent())
    setReady(true)
  }, [])

  const save = useCallback((analytics: boolean) => {
    const value: Consent = { necessary: true, analytics, decidedAt: new Date().toISOString(), version: 1 }
    try {
      window.localStorage.setItem(KEY, JSON.stringify(value))
    } catch {
      /* private mode: the choice lasts for this visit */
    }
    const secure = window.location.protocol === "https:" ? "; Secure" : ""
    document.cookie = `${KEY}=${analytics ? "all" : "necessary"}; Max-Age=${MAX_AGE_DAYS * 86400}; Path=/; SameSite=Lax${secure}`
    setConsent(value)
    setSettingsOpen(false)
  }, [])

  const value = useMemo(
    () => ({ consent, ready, save, openSettings: () => setSettingsOpen(true) }),
    [consent, ready, save],
  )

  return (
    <ConsentContext.Provider value={value}>
      {children}
      {consent?.analytics && <Analytics />}
      {ready && !consent && !settingsOpen && !onGamePage && <CookieBanner onCustomize={() => setSettingsOpen(true)} />}
      <CookieSettings open={settingsOpen} onClose={() => setSettingsOpen(false)} />
    </ConsentContext.Provider>
  )
}

function CookieBanner({ onCustomize }: { onCustomize: () => void }) {
  const { save } = useConsent()
  return (
    <Box
      role="region"
      aria-label="Cookie consent"
      position="fixed"
      insetX={{ base: "3", md: "6" }}
      bottom={{ base: "3", md: "6" }}
      zIndex="overlay"
      maxW="3xl"
      mx="auto"
      bg="bg.panel"
      borderWidth="1px"
      borderColor="brass.border"
      rounded="lg"
      shadow="2xl"
      p={{ base: "4", md: "5" }}
    >
      <Flex direction={{ base: "column", md: "row" }} gap="4" align={{ md: "center" }}>
        <Stack gap="1" flex="1">
          <Text fontFamily="heading" fontSize="lg" color="brass.fg">
            Cookies on this site
          </Text>
          <Text fontSize="sm" color="fg.muted">
            We use only what the site needs to work (like remembering this choice). With your permission we also
            count anonymous page visits to improve the site. No advertising, no tracking across sites. Read our{" "}
            <Link href="#privacy-cookies" color="brass.fg" textDecoration="underline">
              Privacy Policy
            </Link>
            .
          </Text>
        </Stack>
        <HStack gap="2" flexWrap="wrap" justify={{ base: "stretch", md: "flex-end" }}>
          <Button size="sm" variant="ghost" onClick={onCustomize}>
            Customize
          </Button>
          <Button size="sm" variant="outline" colorPalette="brass" onClick={() => save(false)}>
            Necessary only
          </Button>
          <Button size="sm" colorPalette="brass" onClick={() => save(true)}>
            Accept all
          </Button>
        </HStack>
      </Flex>
    </Box>
  )
}

function CookieSettings({ open, onClose }: { open: boolean; onClose: () => void }) {
  const { consent, save } = useConsent()
  const [analytics, setAnalytics] = useState(false)
  useEffect(() => {
    if (open) setAnalytics(consent?.analytics ?? false)
  }, [open, consent])

  return (
    <Dialog.Root open={open} onOpenChange={(e) => !e.open && onClose()} placement="center" size="md">
      <Portal>
        <Dialog.Backdrop />
        <Dialog.Positioner>
          <Dialog.Content bg="bg.panel" borderWidth="1px" borderColor="brass.border" h="auto" maxH="calc(100dvh - 2rem)" mx="4">
            <Dialog.Header>
              <Dialog.Title fontFamily="heading" color="brass.fg">
                Cookie settings
              </Dialog.Title>
            </Dialog.Header>
            <Dialog.Body>
              <Stack gap="5">
                <ConsentRow
                  title="Strictly necessary"
                  text="Remembers your cookie choice. The site cannot work properly without these, so they are always on."
                  checked
                  disabled
                />
                <ConsentRow
                  title="Analytics"
                  text="Vercel Web Analytics counts page views and which pages are visited, without cookies that identify you and without following you to other sites. It helps us see which parts of the site are useful."
                  checked={analytics}
                  onChange={setAnalytics}
                />
              </Stack>
            </Dialog.Body>
            <Dialog.Footer>
              <Button variant="outline" colorPalette="brass" onClick={() => save(false)}>
                Reject optional
              </Button>
              <Button colorPalette="brass" onClick={() => save(analytics)}>
                Save choices
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

function ConsentRow(props: { title: string; text: string; checked: boolean; disabled?: boolean; onChange?: (v: boolean) => void }) {
  return (
    <Flex gap="4" align="flex-start" justify="space-between">
      <Stack gap="1">
        <Text fontWeight="bold">{props.title}</Text>
        <Text fontSize="sm" color="fg.muted">
          {props.text}
        </Text>
      </Stack>
      <Switch.Root
        colorPalette="brass"
        checked={props.checked}
        disabled={props.disabled}
        onCheckedChange={(e) => props.onChange?.(e.checked)}
        mt="1"
      >
        <Switch.HiddenInput aria-label={props.title} />
        <Switch.Control />
      </Switch.Root>
    </Flex>
  )
}

export function CookieSettingsLink() {
  const { openSettings } = useConsent()
  return (
    <Link as="button" fontSize="sm" color="fg.muted" _hover={{ color: "brass.fg" }} onClick={openSettings}>
      Cookie settings
    </Link>
  )
}
