"use client"

import { Box, Button, CloseButton, Container, Drawer, Flex, HStack, IconButton, Link, Portal, Stack, Text } from "@chakra-ui/react"
import Image from "next/image"
import NextLink from "next/link"
import { usePathname } from "next/navigation"
import { useEffect, useState } from "react"
import { LuMenu, LuPlay } from "react-icons/lu"
import { nav, site } from "@/lib/site"

// On the home page the header stays out of the way while the hero is on screen and slides in once the hero has
// scrolled out of view (or the menu is open). Every other page shows it all the time.
export function Header() {
  const home = usePathname() === "/"
  const [heroVisible, setHeroVisible] = useState(home)
  const [open, setOpen] = useState(false)
  useEffect(() => {
    const hero = home ? document.getElementById("hero") : null
    if (!hero) {
      setHeroVisible(false)
      return
    }
    const observer = new IntersectionObserver(([entry]) => setHeroVisible(entry.isIntersecting), { rootMargin: "-80px 0px 0px 0px" })
    observer.observe(hero)
    return () => observer.disconnect()
  }, [home])
  const hidden = home && heroVisible && !open

  return (
    <Box
      as="header"
      position={home ? "fixed" : "sticky"}
      top="0"
      insetX="0"
      zIndex="sticky"
      bg="bg/90"
      backdropFilter="blur(10px)"
      borderBottomWidth="1px"
      borderColor="border"
      transform={hidden ? "translateY(-100%)" : "translateY(0)"}
      opacity={hidden ? 0 : 1}
      visibility={hidden ? "hidden" : "visible"}
      transition="transform 0.35s ease, opacity 0.35s ease, visibility 0.35s"
      aria-hidden={hidden || undefined}
    >
      <Container maxW="7xl" py="3">
        <Flex align="center" justify="space-between" gap="4">
          <Link asChild _hover={{ textDecoration: "none" }} aria-label={`${site.name} home`}>
            <NextLink href="/">
              <HStack gap="2">
                <Image src="/images/icon-192.png" alt="" width={36} height={36} style={{ borderRadius: 8 }} priority />
                <Text fontFamily="heading" fontSize="xl" fontWeight="bold" color="brass.fg" letterSpacing="wide">
                  MindScape 3D
                </Text>
              </HStack>
            </NextLink>
          </Link>

          <HStack as="nav" aria-label="Main" gap="1" display={{ base: "none", lg: "flex" }}>
            {nav.map((item) => (
              <Link
                key={item.href}
                asChild
                px="3"
                py="2"
                rounded="md"
                fontSize="sm"
                color="fg.muted"
                _hover={{ color: "brass.fg", bg: "brass.subtle", textDecoration: "none" }}
              >
                <NextLink href={item.href}>{item.label}</NextLink>
              </Link>
            ))}
          </HStack>

          <HStack gap="2">
            <Button asChild size="sm" colorPalette="brass" display={{ base: "none", sm: "inline-flex" }}>
              <NextLink href="/play">
                <LuPlay /> Play now
              </NextLink>
            </Button>
            <IconButton
              variant="ghost"
              size="sm"
              aria-label="Open menu"
              display={{ base: "inline-flex", lg: "none" }}
              onClick={() => setOpen(true)}
            >
              <LuMenu />
            </IconButton>
          </HStack>
        </Flex>
      </Container>

      <Drawer.Root open={open} onOpenChange={(e) => setOpen(e.open)} placement="end">
        <Portal>
          <Drawer.Backdrop />
          <Drawer.Positioner>
            <Drawer.Content bg="bg.panel">
              <Drawer.Header>
                <Drawer.Title fontFamily="heading" color="brass.fg">
                  MindScape 3D
                </Drawer.Title>
              </Drawer.Header>
              <Drawer.Body>
                <Stack as="nav" aria-label="Mobile" gap="1">
                  {nav.map((item) => (
                    <Link
                      key={item.href}
                      asChild
                      py="3"
                      px="2"
                      rounded="md"
                      fontSize="lg"
                      _hover={{ bg: "brass.subtle", textDecoration: "none" }}
                      onClick={() => setOpen(false)}
                    >
                      <NextLink href={item.href}>{item.label}</NextLink>
                    </Link>
                  ))}
                  <Button asChild mt="4" colorPalette="brass" onClick={() => setOpen(false)}>
                    <NextLink href="/play">
                      <LuPlay /> Play in your browser
                    </NextLink>
                  </Button>
                </Stack>
              </Drawer.Body>
              <Drawer.CloseTrigger asChild>
                <CloseButton size="sm" />
              </Drawer.CloseTrigger>
            </Drawer.Content>
          </Drawer.Positioner>
        </Portal>
      </Drawer.Root>
    </Box>
  )
}
