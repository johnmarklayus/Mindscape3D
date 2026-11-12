import { Box, Container, Flex, HStack, Link, Separator, SimpleGrid, Stack, Text } from "@chakra-ui/react"
import NextLink from "next/link"
import { nav, site } from "@/lib/site"
import { CookieSettingsLink } from "./consent"

export function Footer() {
  return (
    <Box as="footer" bg="bg.subtle" borderTopWidth="1px" borderColor="border" mt="auto">
      <Container maxW="7xl" py={{ base: "10", md: "14" }}>
        <SimpleGrid columns={{ base: 1, md: 3 }} gap="10">
          <Stack gap="3">
            <Text fontFamily="heading" fontSize="2xl" color="brass.fg">
              MindScape 3D
            </Text>
            <Text fontSize="sm" color="fg.muted" maxW="sm">
              {site.tagline} A capstone project of {site.institution} about emotional awareness and coping skills for
              young adults.
            </Text>
            <Text fontSize="xs" color="fg.subtle">
              MindScape 3D is for awareness and learning. It does not replace professional medical advice, diagnosis or
              treatment.
            </Text>
          </Stack>

          <Stack gap="2">
            <Text fontWeight="bold" fontSize="sm" textTransform="uppercase" letterSpacing="widest" color="fg.subtle">
              Explore
            </Text>
            {[...nav, { label: "Play in your browser", href: "/play" }].map((item) => (
              <Link key={item.href} asChild fontSize="sm" color="fg.muted" _hover={{ color: "brass.fg" }}>
                <NextLink href={item.href}>{item.label}</NextLink>
              </Link>
            ))}
          </Stack>

          <Stack gap="2">
            <Text fontWeight="bold" fontSize="sm" textTransform="uppercase" letterSpacing="widest" color="fg.subtle">
              Need someone to talk to?
            </Text>
            <Text fontSize="sm" color="fg.muted">
              NCMH Crisis Hotline (Philippines), 24/7:
            </Text>
            <Text fontFamily="heading" fontSize="2xl" color="brass.fg">
              <Link href="tel:1553" color="inherit">
                1553
              </Link>
            </Text>
            <Text fontSize="sm" color="fg.muted">
              or 1800-1888-1553 · 0917-899-8727 · 0966-351-4518. If you are in immediate danger, call your local
              emergency number.
            </Text>
          </Stack>
        </SimpleGrid>

        <Separator my="8" borderColor="border" />

        <Flex direction={{ base: "column", md: "row" }} gap="4" justify="space-between" align={{ md: "center" }}>
          <Text fontSize="sm" color="fg.subtle">
            © {new Date().getFullYear()} The MindScape 3D Team · {site.institution}
          </Text>
          <HStack gap="5" flexWrap="wrap">
            <Link href="#privacy" fontSize="sm" color="fg.muted" _hover={{ color: "brass.fg" }}>
              Privacy Policy
            </Link>
            <Link href="#terms" fontSize="sm" color="fg.muted" _hover={{ color: "brass.fg" }}>
              Terms and Conditions
            </Link>
            <CookieSettingsLink />
          </HStack>
        </Flex>
      </Container>
    </Box>
  )
}
