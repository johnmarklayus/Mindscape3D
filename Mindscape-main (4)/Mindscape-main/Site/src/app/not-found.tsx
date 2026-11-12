import { Button, Container, Heading, Stack, Text } from "@chakra-ui/react"
import NextLink from "next/link"

export default function NotFound() {
  return (
    <Container maxW="2xl" py="32">
      <Stack align="center" textAlign="center" gap="4">
        <Text fontSize="sm" letterSpacing="0.2em" textTransform="uppercase" color="brass.fg">
          Page not found
        </Text>
        <Heading as="h1" fontFamily="heading" fontSize="4xl">
          This path doesn't lead anywhere yet.
        </Heading>
        <Text color="fg.muted">Take a breath, and head back to the start.</Text>
        <Button asChild colorPalette="brass">
          <NextLink href="/">Back to the home page</NextLink>
        </Button>
      </Stack>
    </Container>
  )
}
