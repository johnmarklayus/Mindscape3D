import { Badge, Box, Card, Flex, Heading, Icon, SimpleGrid, Stack, Text } from "@chakra-ui/react"
import Image from "next/image"
import {
  LuBookOpen,
  LuCloud,
  LuGauge,
  LuHeartHandshake,
  LuMap,
  LuMonitorSmartphone,
  LuNotebookPen,
  LuScale,
  LuSplit,
  LuWind,
} from "react-icons/lu"
import { Section } from "./section"

const purpose = [
  {
    title: "Notice what you feel",
    text: "Everyday moments (a deadline, a comparison, a quiet dinner table) are played out from the inside, so players can recognise stress and name the feeling behind it.",
  },
  {
    title: "Practise a way through",
    text: "Each episode pairs a hard moment with a coping skill drawn from cognitive behavioural approaches: slowing the breath, grounding in the present, and testing a worried thought against the facts.",
  },
  {
    title: "Reflect at your own pace",
    text: "After every episode the player writes in a private journal and checks in on how they feel. There is no score to chase and no wrong answer.",
  },
]

const features = [
  { icon: LuMap, title: "A whole town to explore", text: "Walk Joey's home, school, dormitory and city streets in third or first person, with neighbours, classmates and traffic going about their day." },
  { icon: LuSplit, title: "Choices that stay with you", text: "What you say to friends and family is remembered, and earlier decisions return later in the story as small changes in Joey's inner voice." },
  { icon: LuWind, title: "Guided breathing", text: "A calm, animated breathing exercise you can open whenever the moment gets heavy, inside the story or on its own." },
  { icon: LuScale, title: "The Worry Courtroom", text: "Put an anxious thought on trial: weigh the evidence, hear a friend's view, and choose a more balanced thought and one small next step." },
  { icon: LuHeartHandshake, title: "5-4-3-2-1 grounding", text: "Tap the things you can see, hear and touch around you to bring your attention back to the present." },
  { icon: LuGauge, title: "Stress meter and check-ins", text: "A gentle meter shows how pressure builds and eases, with short check-ins that ask how you are really doing." },
  { icon: LuNotebookPen, title: "Reflection journal", text: "Write about each episode and answer a short self-assessment. Your entries are kept on your device, or in your account if you sign in." },
  { icon: LuBookOpen, title: "Play as a boy or a girl", text: "Choose who Joey is, pick a name, and see the world through their eyes across three chapters and seventeen episodes." },
  { icon: LuCloud, title: "Your progress, anywhere", text: "Play offline, or create a free account to keep your progress and journal in sync across devices." },
  { icon: LuMonitorSmartphone, title: "Cross-platform", text: "Play in the browser with nothing to install, or download for Windows, macOS and Android, with touch controls on phones and tablets." },
]

export function Overview() {
  return (
    <Section
      id="overview"
      eyebrow="Project overview"
      title="A safe place to understand stress"
      intro={
        <>
          MindScape 3D is <b>A Cross-Platform Online Interactive Simulation Game for Emotional Awareness and Coping
          Skill Development for Young Adults</b>. It turns the pressure of studies, family expectations and friendships
          into a story you can walk through, so the skills for handling it feel familiar before you need them.
        </>
      }
    >
      <SimpleGrid columns={{ base: 1, md: 3 }} gap="6">
        {purpose.map((p, i) => (
          <Card.Root key={p.title} bg="bg.panel" borderColor="border" variant="outline">
            <Card.Body gap="3">
              <Text fontFamily="heading" fontSize="4xl" color="brass.solid" lineHeight="1">
                {String(i + 1).padStart(2, "0")}
              </Text>
              <Card.Title fontFamily="heading" fontSize="xl">
                {p.title}
              </Card.Title>
              <Card.Description color="fg.muted" fontSize="md">
                {p.text}
              </Card.Description>
            </Card.Body>
          </Card.Root>
        ))}
      </SimpleGrid>
    </Section>
  )
}

export function Features() {
  return (
    <Section
      id="features"
      tone="subtle"
      eyebrow="Features"
      title="What's inside the game"
      intro="Story, exploration and evidence-informed coping tools, wrapped in a warm low-poly world."
    >
      <SimpleGrid columns={{ base: 1, sm: 2, lg: 3, xl: 5 }} gap="5">
        {features.map((f) => (
          <Card.Root key={f.title} bg="bg.panel" variant="outline" borderColor="border" _hover={{ borderColor: "brass.border", transform: "translateY(-2px)" }} transition="all 0.2s">
            <Card.Body gap="3">
              <Flex boxSize="11" rounded="lg" bg="brass.subtle" color="brass.fg" align="center" justify="center" borderWidth="1px" borderColor="brass.muted">
                <Icon boxSize="5">
                  <f.icon />
                </Icon>
              </Flex>
              <Heading as="h3" fontFamily="heading" fontSize="lg" fontWeight="semibold">
                {f.title}
              </Heading>
              <Text color="fg.muted" fontSize="sm">
                {f.text}
              </Text>
            </Card.Body>
          </Card.Root>
        ))}
      </SimpleGrid>
    </Section>
  )
}

const chapters = [
  { img: "/images/tutorial.jpg", label: "Tutorial", title: "Getting Started", episodes: 1, text: "Learn to move, look around, talk to people and open your journal, at your own pace." },
  { img: "/images/ch1.jpg", label: "Chapter 1", title: "Academic Pressure", episodes: 4, text: "One school deadline, from the morning alarm to the classroom, the cafeteria and a quiet night in the dormitory." },
  { img: "/images/ch2.jpg", label: "Chapter 2", title: "Family Expectations", episodes: 5, text: "An examination day that doesn't go as planned, a family dinner, and the keepsakes that remind Joey who they are." },
  { img: "/images/ch3.jpg", label: "Chapter 3", title: "Social Dynamics", episodes: 8, text: "A reunion with old friends, the fear of being left behind, and a group photograph worth stepping into." },
]

export function Chapters() {
  return (
    <Section id="chapters" eyebrow="The story" title="Three chapters, seventeen episodes" intro="Each chapter is a different kind of pressure. Play them in order, take a break whenever you like, and return to where you left off.">
      <SimpleGrid columns={{ base: 1, sm: 2, lg: 4 }} gap="6">
        {chapters.map((c) => (
          <Card.Root key={c.title} overflow="hidden" bg="bg.panel" variant="outline" borderColor="border">
            <Box position="relative" aspectRatio={16 / 9}>
              <Image src={c.img} alt={`${c.label}: ${c.title} in MindScape 3D`} fill sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 25vw" style={{ objectFit: "cover" }} />
            </Box>
            <Card.Body gap="2">
              <Flex justify="space-between" align="center">
                <Text fontSize="xs" fontWeight="bold" letterSpacing="0.18em" textTransform="uppercase" color="brass.fg">
                  {c.label}
                </Text>
                <Badge variant="subtle" colorPalette="brass">
                  {c.episodes} {c.episodes === 1 ? "episode" : "episodes"}
                </Badge>
              </Flex>
              <Heading as="h3" fontFamily="heading" fontSize="xl" fontWeight="semibold">
                {c.title}
              </Heading>
              <Text fontSize="sm" color="fg.muted">
                {c.text}
              </Text>
            </Card.Body>
          </Card.Root>
        ))}
      </SimpleGrid>

      <SimpleGrid columns={{ base: 2, md: 5 }} gap="3" mt="8" aria-label="Screenshots">
        {[
          ["/images/g-cafeteria.jpg", "The school cafeteria at lunch"],
          ["/images/g-dorm.jpg", "The dormitory study room"],
          ["/images/g-bedroom.jpg", "Joey's bedroom at night"],
          ["/images/g-reunion.jpg", "The reunion hall"],
          ["/images/g-park.jpg", "A walk through the city park"],
        ].map(([src, alt]) => (
          <Box key={src} position="relative" aspectRatio={16 / 9} rounded="md" overflow="hidden" borderWidth="1px" borderColor="border">
            <Image src={src} alt={`${alt} (MindScape 3D screenshot)`} fill sizes="(max-width: 768px) 50vw, 20vw" style={{ objectFit: "cover" }} />
          </Box>
        ))}
      </SimpleGrid>
      <Stack mt="3" align="center">
        <Text fontSize="xs" color="fg.subtle">
          Screenshots from version 0.3.0.
        </Text>
      </Stack>
    </Section>
  )
}
