import { Flex } from "@chakra-ui/react"
import type { ReactNode } from "react"
import { Footer } from "@/components/footer"
import { Header } from "@/components/header"

// The website's pages: header, content, footer. (/play is outside this group, so the game has the whole screen.)
export default function SiteLayout({ children }: { children: ReactNode }) {
  return (
    <Flex direction="column" minH="100dvh">
      <Header />
      <Flex as="main" id="main" direction="column" flex="1">
        {children}
      </Flex>
      <Footer />
    </Flex>
  )
}
