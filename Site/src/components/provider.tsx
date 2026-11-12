"use client"

import { ChakraProvider } from "@chakra-ui/react"
import type { ReactNode } from "react"
import { system } from "@/theme"
import { ConsentProvider } from "./consent"
import { EmotionRegistry } from "./emotion-registry"
import { LegalModal } from "./legal-modal"

// Chakra UI (always dark: <html class="dark"> is set in the root layout) and the cookie-consent state every page can read.
export function Provider({ children }: { children: ReactNode }) {
  return (
    <EmotionRegistry>
      <ChakraProvider value={system}>
        <ConsentProvider>{children}</ConsentProvider>
        <LegalModal />
      </ChakraProvider>
    </EmotionRegistry>
  )
}
