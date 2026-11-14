/** Onboarding topics: one Markdown file per topic under src/content/onboarding, ordered by filename. */

export interface OnboardingTopic {
  id: string
  /** Sidebar section (accordion). */
  group: string
  /** Sidebar label. */
  nav: string
  body: string
}

export interface OnboardingGroup {
  title: string
  topics: OnboardingTopic[]
}

const files = import.meta.glob<string>("../content/onboarding/*.md", {
  query: "?raw",
  import: "default",
  eager: true,
})

function parse(file: string, raw: string): OnboardingTopic {
  const match = /^---\n([\s\S]*?)\n---\n([\s\S]*)$/.exec(raw.replace(/\r\n/g, "\n"))
  if (!match) throw new Error(`${file}: missing front matter`)
  const fields = Object.fromEntries(
    match[1].split("\n").map((line) => {
      const i = line.indexOf(":")
      return [line.slice(0, i).trim(), line.slice(i + 1).trim()]
    }),
  )
  for (const key of ["id", "group", "nav"]) {
    if (!fields[key]) throw new Error(`${file}: front matter is missing "${key}"`)
  }
  return { id: fields.id, group: fields.group, nav: fields.nav, body: match[2].trim() }
}

export const onboardingTopics: OnboardingTopic[] = Object.entries(files)
  .sort(([a], [b]) => a.localeCompare(b))
  .map(([file, raw]) => parse(file, raw))

export const onboardingGroups: OnboardingGroup[] = []
for (const topic of onboardingTopics) {
  let group = onboardingGroups.find((g) => g.title === topic.group)
  if (!group) onboardingGroups.push((group = { title: topic.group, topics: [] }))
  group.topics.push(topic)
}
