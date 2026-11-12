import { Badge, Box, Button, Container, Heading, HStack, Stack, Text, VisuallyHidden } from "@chakra-ui/react"
import Image from "next/image"
import NextLink from "next/link"
import { FaAndroid, FaApple, FaGlobe, FaWindows } from "react-icons/fa6"
import { LuChevronDown, LuDownload, LuPlay } from "react-icons/lu"
import { site } from "@/lib/site"
import { AnimatedLogo, Fireflies } from "./animated-logo"

// The main menu's sunset art with its night-teal veil, the glowing title, and the two calls to action.
// The hero is always dark (it sits on a picture), whichever color mode the rest of the page uses.
export function Hero() {
  return (
    <Box as="section" id="hero" aria-labelledby="hero-title" position="relative" overflow="hidden" minH="100dvh" display="flex" alignItems="center">
      <Box position="absolute" inset="0" css={{ animation: "ms-kenburns 30s ease-in-out infinite alternate", "@media (prefers-reduced-motion: reduce)": { animation: "none" } }}>
      <Image
        src="/images/hero.jpg"
        alt="Joey and a friend sit on a hill at sunset, looking over the low-poly town of MindScape 3D."
        fill
        priority
        sizes="100vw"
        quality={85}
        style={{ objectFit: "cover", objectPosition: "center 40%" }}
      />
      </Box>
      <Box
        position="absolute"
        inset="0"
        bgGradient="to-b"
        gradientFrom="rgba(13,20,24,0.35)"
        gradientVia="rgba(13,20,24,0.55)"
        gradientTo="rgba(13,20,24,0.92)"
      />
      <Fireflies />
      <Container maxW="5xl" position="relative" pt={{ base: "16", md: "20" }} pb={{ base: "28", md: "32" }}>
        <Stack align="center" textAlign="center" gap={{ base: "5", md: "7" }} color="#f0e4cc">
          <Heading as="h1" id="hero-title" m="0">
            <VisuallyHidden>{site.name}: {site.tagline}</VisuallyHidden>
            <AnimatedLogo width={{ base: "300px", sm: "440px", md: "620px" }} />
          </Heading>
          <Text fontSize={{ base: "md", md: "xl" }} maxW="2xl" color="#f0e4cc" textShadow="0 1px 10px rgba(0,0,0,0.7)">
            A free story game about the pressures of school, family and friendship, and the small skills that help you
            breathe through them. Play as Joey, make your own choices, and find your own pace.
          </Text>
          <HStack gap="3" flexWrap="wrap" justify="center" pt="2">
            <Button asChild size="2xl" h={{ base: "16", md: "20" }} minW={{ base: "40", md: "56" }} px={{ base: "8", md: "12" }} fontSize={{ base: "xl", md: "2xl" }} fontWeight="bold" rounded="lg" colorPalette="brass" bg="#d8b46c" color="#211c18" _hover={{ bg: "#ffe2a0", transform: "translateY(-2px)" }} boxShadow="0 10px 30px rgba(216,180,108,0.35)" transition="all 0.2s" css={{ "& svg": { width: "1.4em", height: "1.4em" } }}>
              <NextLink href="/play">
                <LuPlay /> Play
              </NextLink>
            </Button>
            <Button
              asChild
              size="2xl"
              h={{ base: "16", md: "20" }}
              minW={{ base: "40", md: "56" }}
              px={{ base: "8", md: "12" }}
              fontSize={{ base: "xl", md: "2xl" }}
              fontWeight="bold"
              rounded="lg"
              borderWidth="2px"
              transition="all 0.2s"
              css={{ "& svg": { width: "1.4em", height: "1.4em" } }}
              variant="outline"
              color="#f0e4cc"
              borderColor="#bda477"
              bg="rgba(33,28,24,0.55)"
              _hover={{ bg: "rgba(48,33,22,0.9)", borderColor: "#ffe2a0", transform: "translateY(-2px)" }}
            >
              <a href="#download">
                <LuDownload /> Download
              </a>
            </Button>
          </HStack>
          <HStack gap="2" flexWrap="wrap" justify="center" pt="1" aria-label="Available on">
            {[
              { icon: <FaWindows />, label: "Windows" },
              { icon: <FaApple />, label: "macOS" },
              { icon: <FaAndroid />, label: "Android" },
              { icon: <FaGlobe />, label: "Web" },
            ].map((p) => (
              <Badge key={p.label} size="lg" variant="outline" color="#f0e4cc" borderColor="rgba(189,164,119,0.6)" bg="rgba(18,24,27,0.5)" gap="1.5" px="3">
                {p.icon} {p.label}
              </Badge>
            ))}
            <Badge size="lg" bg="rgba(216,180,108,0.2)" color="#ffe2a0" px="3">
              Free · v{site.version}
            </Badge>
          </HStack>
        </Stack>
      </Container>
      {/* Scroll cue: a mouse with a rolling wheel and two falling chevrons. */}
      <Box
        asChild
        position="absolute"
        bottom={{ base: "4", md: "8" }}
        left="50%"
        transform="translateX(-50%)"
        color="#f0e4cc"
        opacity={0.85}
        _hover={{ opacity: 1, color: "#ffe2a0" }}
        transition="color 0.2s, opacity 0.2s"
        textAlign="center"
      >
        <a href="#overview" aria-label="Scroll down to learn more">
          <Stack align="center" gap="1">
            <Box w="26px" h="42px" borderWidth="2px" borderColor="currentColor" rounded="full" position="relative">
              <Box
                position="absolute"
                left="50%"
                top="8px"
                w="4px"
                h="8px"
                ml="-2px"
                rounded="full"
                bg="currentColor"
                css={{ animation: "ms-wheel 1.8s ease-in-out infinite", "@media (prefers-reduced-motion: reduce)": { animation: "none" } }}
              />
            </Box>
            <Stack gap="0" align="center" lineHeight="0">
              {[0, 0.2].map((delay) => (
                <Box key={delay} css={{ animation: `ms-chevron 1.8s ease-in-out ${delay}s infinite`, "@media (prefers-reduced-motion: reduce)": { animation: "none" } }}>
                  <LuChevronDown size={18} />
                </Box>
              ))}
            </Stack>
            <Text fontSize="xs" letterSpacing="0.25em" textTransform="uppercase" display={{ base: "none", md: "block" }}>
              Scroll
            </Text>
          </Stack>
        </a>
      </Box>
    </Box>
  )
}
