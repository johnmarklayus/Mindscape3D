import { Box, Card, Flex, Heading, HStack, Icon, Link, SimpleGrid, Stack, Tag, Text } from "@chakra-ui/react"
import { LuExternalLink, LuGraduationCap, LuPhone, LuUsers, LuWrench } from "react-icons/lu"
import { site } from "@/lib/site"
import { Section } from "./section"

const team = [
  { role: "Project Manager", names: ["John Mark V. Layus"] },
  { role: "Lead Developer / Programmer", names: ["Kenn O. Occeño"] },
  { role: "Lead 3D Artist & Environment Designer", names: ["Mark Jason B. Dela Cruz", "Michael Bryan M. Amelanto"] },
  { role: "UI & Graphic Design · Narrative Design · QA", names: ["All team members"] },
]

const tools = ["Unity", "Blender", "Visual Studio Code", "Audacity", "Supabase"]

export function About() {
  return (
    <Section
      id="about"
      eyebrow="About"
      title="Made by students, for young adults"
      intro={
        <>
          MindScape 3D is a capstone project of {site.institution}. We built it because pressure from school, family
          and friends is something almost every young adult carries, and a game is a gentle, private way to look at it
          and practise what helps.
        </>
      }
    >
      <SimpleGrid columns={{ base: 1, lg: 3 }} gap="6">
        <Card.Root bg="bg.panel" variant="outline" borderColor="border" gridColumn={{ lg: "span 2" }}>
          <Card.Body gap="5">
            <CardTitle icon={LuUsers}>The team</CardTitle>
            <SimpleGrid columns={{ base: 1, sm: 2 }} gap="5">
              {team.map((t) => (
                <Stack key={t.role} gap="1">
                  <Text fontSize="xs" fontWeight="bold" letterSpacing="0.14em" textTransform="uppercase" color="brass.fg">
                    {t.role}
                  </Text>
                  {t.names.map((n) => (
                    <Text key={n} fontFamily="heading" fontSize="lg">
                      {n}
                    </Text>
                  ))}
                </Stack>
              ))}
            </SimpleGrid>
            <Box h="1px" bg="border" />
            <SimpleGrid columns={{ base: 1, sm: 2 }} gap="5">
              <Stack gap="1">
                <HStack color="brass.fg" gap="2">
                  <Icon boxSize="4">
                    <LuGraduationCap />
                  </Icon>
                  <Text fontSize="xs" fontWeight="bold" letterSpacing="0.14em" textTransform="uppercase">
                    Capstone adviser
                  </Text>
                </HStack>
                <Text fontFamily="heading" fontSize="lg">
                  Prince Aron E. Chavez
                </Text>
              </Stack>
              <Stack gap="1">
                <Text fontSize="xs" fontWeight="bold" letterSpacing="0.14em" textTransform="uppercase" color="brass.fg">
                  Institution
                </Text>
                <Text fontFamily="heading" fontSize="lg">
                  {site.institution}
                </Text>
              </Stack>
            </SimpleGrid>
            <Stack gap="2">
              <HStack color="brass.fg" gap="2">
                <Icon boxSize="4">
                  <LuWrench />
                </Icon>
                <Text fontSize="xs" fontWeight="bold" letterSpacing="0.14em" textTransform="uppercase">
                  Built with
                </Text>
              </HStack>
              <HStack gap="2" flexWrap="wrap">
                {tools.map((t) => (
                  <Tag.Root key={t} colorPalette="brass" variant="subtle" size="lg">
                    <Tag.Label>{t}</Tag.Label>
                  </Tag.Root>
                ))}
              </HStack>
            </Stack>
            <Text fontSize="sm" color="fg.muted">
              Every model, interior, character and interface in the game was made by the team, and we are grateful to
              our families, friends and the faculty of {site.institution} for their guidance and support.
            </Text>
          </Card.Body>
        </Card.Root>

        <Card.Root bg="bg.panel" variant="outline" borderColor="rust.border" id="help">
          <Card.Body gap="4">
            <CardTitle icon={LuPhone}>If you need help now</CardTitle>
            <Text color="fg.muted" fontSize="sm">
              MindScape 3D is a learning experience, not therapy. If you or someone you know is struggling, please reach
              out. You are not alone.
            </Text>
            <Hotline name="National Center for Mental Health (24/7)" numbers="1553 · 1800-1888-1553 · 0917-899-8727 · 0966-351-4518" href="https://ncmh.gov.ph/" />
            <Hotline name="In Touch Community Services (free, 24/7)" numbers="+63 2 8893 7603 · +63 917 800 1123" href="https://in-touch.org/" />
            <Hotline name="Philippine Mental Health Association" numbers="Remote support; see current schedule" href="https://www.pmha.org.ph/" />
            <Text fontSize="xs" color="fg.subtle">
              Numbers and hours can change; check each provider's page. In an emergency, call your local emergency
              number.
            </Text>
          </Card.Body>
        </Card.Root>
      </SimpleGrid>
    </Section>
  )
}

function CardTitle({ icon: I, children }: { icon: typeof LuUsers; children: string }) {
  return (
    <Flex align="center" gap="2">
      <Icon color="brass.fg" boxSize="5">
        <I />
      </Icon>
      <Heading as="h3" fontFamily="heading" fontSize="xl" fontWeight="semibold">
        {children}
      </Heading>
    </Flex>
  )
}

function Hotline({ name, numbers, href }: { name: string; numbers: string; href: string }) {
  return (
    <Stack gap="0.5">
      <Text fontWeight="bold">{name}</Text>
      <Text fontSize="sm" color="fg.muted">
        {numbers}
      </Text>
      <Link href={href} target="_blank" rel="noopener noreferrer" fontSize="sm" color="brass.fg">
        Visit website <LuExternalLink />
      </Link>
    </Stack>
  )
}
