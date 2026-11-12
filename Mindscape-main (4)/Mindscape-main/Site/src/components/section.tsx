import { Box, Container, Heading, Stack, Text } from "@chakra-ui/react"
import type { ReactNode } from "react"

// A landing-page section with the game's heading style: a small gold eyebrow, a serif title and a flourish rule.
export function Section(props: {
  id: string
  eyebrow: string
  title: string
  intro?: ReactNode
  children: ReactNode
  tone?: "plain" | "subtle"
}) {
  return (
    <Box
      as="section"
      id={props.id}
      aria-labelledby={`${props.id}-title`}
      bg={props.tone === "subtle" ? "bg.subtle" : "bg"}
      py={{ base: "16", md: "24" }}
    >
      <Container maxW="7xl">
        <Stack gap="3" textAlign="center" align="center" mb={{ base: "10", md: "14" }}>
          <Text fontSize="sm" fontWeight="bold" letterSpacing="0.2em" textTransform="uppercase" color="brass.fg">
            {props.eyebrow}
          </Text>
          <Heading as="h2" id={`${props.id}-title`} fontFamily="heading" fontWeight="semibold" fontSize={{ base: "3xl", md: "5xl" }} lineHeight="1.15">
            {props.title}
          </Heading>
          <Flourish />
          {props.intro && (
            <Text fontSize={{ base: "md", md: "lg" }} color="fg.muted" maxW="3xl">
              {props.intro}
            </Text>
          )}
        </Stack>
        {props.children}
      </Container>
    </Box>
  )
}

// The thin brass rule with a diamond, after the menu's page-title flourish.
export function Flourish() {
  return (
    <Box aria-hidden display="flex" alignItems="center" gap="2" color="brass.solid">
      <Box h="1px" w="12" bg="currentColor" opacity={0.6} />
      <Box boxSize="2" bg="currentColor" transform="rotate(45deg)" />
      <Box h="1px" w="12" bg="currentColor" opacity={0.6} />
    </Box>
  )
}
