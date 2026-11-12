"use client"

import { Badge, Box, Button, Card, Flex, Heading, HStack, Icon, SimpleGrid, Stack, Table, Tabs, Text } from "@chakra-ui/react"
import NextLink from "next/link"
import type { IconType } from "react-icons"
import { FaAndroid, FaApple, FaGlobe, FaWindows } from "react-icons/fa6"
import { LuCalendar, LuDownload, LuHardDrive, LuPlay, LuTag } from "react-icons/lu"
import { downloads, type Download, type PlatformId, type Requirements } from "@/data/downloads"
import { Section } from "./section"

const icons: Record<PlatformId, IconType> = { windows: FaWindows, macos: FaApple, android: FaAndroid, web: FaGlobe }

export function Downloads() {
  return (
    <Section
      id="download"
      tone="subtle"
      eyebrow="Download"
      title="Play on your device"
      intro="MindScape 3D is free. Download it for your computer or phone, or play straight away in your browser."
    >
      <SimpleGrid columns={{ base: 1, md: 2 }} gap="6">
        {downloads.map((d) => (
          <DownloadCard key={d.id} d={d} />
        ))}
      </SimpleGrid>
      <Text mt="6" fontSize="sm" color="fg.subtle" textAlign="center">
        Sizes are for the download itself; the installed game needs a little more room. Your saves stay on your device
        unless you sign in.
      </Text>
    </Section>
  )
}

function DownloadCard({ d }: { d: Download }) {
  const PlatformIcon = icons[d.id]
  const available = d.url !== ""
  const web = d.id === "web"
  return (
    <Card.Root bg="bg.panel" variant="outline" borderColor={web ? "brass.border" : "border"} id={`download-${d.id}`}>
      <Card.Body gap="5">
        <Flex gap="4" align="center">
          <Flex boxSize="14" rounded="xl" bg="brass.subtle" color="brass.fg" align="center" justify="center" borderWidth="1px" borderColor="brass.muted" flexShrink={0}>
            <Icon boxSize="7">
              <PlatformIcon />
            </Icon>
          </Flex>
          <Stack gap="0.5" flex="1" minW="0">
            <Heading as="h3" fontFamily="heading" fontSize="2xl" fontWeight="semibold">
              {d.name}
            </Heading>
            <Text fontSize="sm" color="fg.muted" truncate>
              {d.file}
            </Text>
          </Stack>
          {web && (
            <Badge colorPalette="brass" variant="solid" display={{ base: "none", sm: "inline-flex" }}>
              No install
            </Badge>
          )}
        </Flex>

        <HStack gap="2" flexWrap="wrap">
          <Meta icon={LuTag} label="Version" value={`v${d.version}`} />
          <Meta icon={LuHardDrive} label="Size" value={d.size} />
          <Meta icon={LuCalendar} label="Released" value={formatDate(d.date)} />
        </HStack>

        <Tabs.Root defaultValue="minimum" variant="line" colorPalette="brass" size="sm">
          <Tabs.List>
            <Tabs.Trigger value="minimum">Minimum</Tabs.Trigger>
            <Tabs.Trigger value="recommended">Recommended</Tabs.Trigger>
          </Tabs.List>
          <Tabs.Content value="minimum">
            <Specs rows={d.minimum} caption={`Minimum system requirements for ${d.name}`} />
          </Tabs.Content>
          <Tabs.Content value="recommended">
            <Specs rows={d.recommended} caption={`Recommended system requirements for ${d.name}`} />
          </Tabs.Content>
        </Tabs.Root>

        {d.note && (
          <Text fontSize="sm" color="fg.muted">
            {d.note}
          </Text>
        )}

        <Box mt="auto">
          {web ? (
            <Button asChild colorPalette="brass" w="full" size="lg">
              <NextLink href="/play">
                <LuPlay /> Play in your browser
              </NextLink>
            </Button>
          ) : available ? (
            <Button asChild colorPalette="brass" w="full" size="lg">
              <a href={d.url} rel="noopener" download>
                <LuDownload /> Download for {d.name} · {d.size}
              </a>
            </Button>
          ) : (
            <Button w="full" size="lg" variant="outline" colorPalette="brass" disabled aria-disabled>
              Coming soon
            </Button>
          )}
        </Box>
      </Card.Body>
    </Card.Root>
  )
}

function Meta({ icon: I, label, value }: { icon: IconType; label: string; value: string }) {
  return (
    <HStack gap="1.5" px="2.5" py="1" rounded="md" bg="bg.muted" fontSize="sm" title={label}>
      <Icon color="brass.fg" boxSize="3.5">
        <I />
      </Icon>
      <Text as="span" color="fg.subtle">
        {label}:
      </Text>
      <Text as="span" fontWeight="bold">
        {value}
      </Text>
    </HStack>
  )
}

function Specs({ rows, caption }: { rows: Requirements; caption: string }) {
  return (
    <Table.Root size="sm" variant="line" mt="1">
      <Table.Caption srOnly>{caption}</Table.Caption>
      <Table.Body>
        {rows.map((r) => (
          <Table.Row key={r.label} bg="transparent">
            <Table.Cell color="fg.subtle" w="32%" ps="0" borderColor="border.muted" verticalAlign="top">
              {r.label}
            </Table.Cell>
            <Table.Cell pe="0" borderColor="border.muted">
              {r.value}
            </Table.Cell>
          </Table.Row>
        ))}
      </Table.Body>
    </Table.Root>
  )
}

function formatDate(iso: string) {
  return new Date(`${iso}T00:00:00Z`).toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric", timeZone: "UTC" })
}
