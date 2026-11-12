"use client"

import { Alert, Box, Button, chakra, Card, Checkbox, Field, Input, Link, NativeSelect, SimpleGrid, Stack, Text, Textarea } from "@chakra-ui/react"
import { useState, type FormEvent } from "react"
import { LuSend } from "react-icons/lu"
import { BUG_TOPIC, topics } from "@/lib/contact"
import { site } from "@/lib/site"
import { ScreenshotPicker, type Shot } from "./screenshot-picker"
import { Section } from "./section"

type Status = { kind: "idle" } | { kind: "sending" } | { kind: "sent" } | { kind: "error"; message: string }
type Errors = Partial<Record<"name" | "email" | "message" | "agree", string>>

export function Contact() {
  const [status, setStatus] = useState<Status>({ kind: "idle" })
  const [errors, setErrors] = useState<Errors>({})
  const [topic, setTopic] = useState<string>(topics[0])
  const [shots, setShots] = useState<Shot[]>([])
  const bug = topic === BUG_TOPIC

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    const form = e.currentTarget
    const formData = new FormData(form)
    const data = Object.fromEntries(formData) as Record<string, string>
    const next: Errors = {}
    if (!data.name?.trim()) next.name = "Please tell us your name."
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.email ?? "")) next.email = "Please enter a valid email address."
    if ((data.message ?? "").trim().length < 10) next.message = "Please write at least a sentence (10 characters)."
    if (data.agree !== "on") next.agree = "Please agree so we can use your details to reply."
    setErrors(next)
    if (Object.keys(next).length) return

    setStatus({ kind: "sending" })
    try {
      // Sent as multipart form data so bug reports can carry their screenshots.
      if (bug) shots.forEach((s) => formData.append("screenshots", s.file, s.file.name))
      const res = await fetch("/api/contact", { method: "POST", body: formData })
      const body = (await res.json().catch(() => ({}))) as { error?: string }
      if (!res.ok) throw new Error(body.error || "Something went wrong. Please try again.")
      form.reset()
      setTopic(topics[0])
      shots.forEach((s) => URL.revokeObjectURL(s.url))
      setShots([])
      setStatus({ kind: "sent" })
    } catch (err) {
      setStatus({ kind: "error", message: err instanceof Error ? err.message : "Something went wrong." })
    }
  }

  return (
    <Section
      id="contact"
      tone="subtle"
      eyebrow="Contact"
      title="Get in touch"
      intro="Questions, feedback, a bug you found, or interest from your school? Send us a message and the team will reply by email."
    >
      <Card.Root maxW="3xl" mx="auto" bg="bg.panel" variant="outline" borderColor="border">
        <Card.Body>
          <chakra.form onSubmit={onSubmit} noValidate aria-describedby="contact-note">
            <Stack gap="5">
              {/* Hidden from people; bots that fill every field are dropped by the server. */}
              <Box position="absolute" left="-9999px" aria-hidden>
                <label>
                  Leave this empty
                  <input type="text" name="website" tabIndex={-1} autoComplete="off" />
                </label>
              </Box>
              <SimpleGrid columns={{ base: 1, md: 2 }} gap="5">
                <Field.Root required invalid={!!errors.name}>
                  <Field.Label>
                    Name <Field.RequiredIndicator />
                  </Field.Label>
                  <Input name="name" autoComplete="name" maxLength={100} placeholder="Your name" />
                  <Field.ErrorText>{errors.name}</Field.ErrorText>
                </Field.Root>
                <Field.Root required invalid={!!errors.email}>
                  <Field.Label>
                    Email <Field.RequiredIndicator />
                  </Field.Label>
                  <Input name="email" type="email" autoComplete="email" maxLength={200} placeholder="you@example.com" />
                  <Field.ErrorText>{errors.email}</Field.ErrorText>
                </Field.Root>
              </SimpleGrid>
              <Field.Root>
                <Field.Label>Topic</Field.Label>
                <NativeSelect.Root>
                  <NativeSelect.Field name="topic" value={topic} onChange={(e) => setTopic(e.currentTarget.value)}>
                    {topics.map((t) => (
                      <option key={t} value={t}>
                        {t}
                      </option>
                    ))}
                  </NativeSelect.Field>
                  <NativeSelect.Indicator />
                </NativeSelect.Root>
              </Field.Root>
              <Field.Root required invalid={!!errors.message}>
                <Field.Label>
                  Message <Field.RequiredIndicator />
                </Field.Label>
                <Textarea name="message" rows={6} maxLength={4000} placeholder={bug ? "What happened, what you expected, and which episode or screen you were on." : "How can we help?"} />
                <Field.HelperText>Please don't include health details you wouldn't want to share by email.</Field.HelperText>
                <Field.ErrorText>{errors.message}</Field.ErrorText>
              </Field.Root>
              {bug && <ScreenshotPicker shots={shots} onChange={setShots} />}
              <Field.Root invalid={!!errors.agree}>
                <Checkbox.Root name="agree" colorPalette="brass" alignItems="flex-start">
                  <Checkbox.HiddenInput />
                  <Checkbox.Control mt="0.5" />
                  <Checkbox.Label fontWeight="normal" color="fg.muted">
                    I agree that the MindScape 3D team may use my name and email to answer this message, as described in
                    the{" "}
                    <Link href="#privacy-contact-form" color="brass.fg" textDecoration="underline">
                      Privacy Policy
                    </Link>
                    .
                  </Checkbox.Label>
                </Checkbox.Root>
                <Field.ErrorText>{errors.agree}</Field.ErrorText>
              </Field.Root>

              {status.kind === "sent" && (
                <Alert.Root status="success" variant="subtle">
                  <Alert.Indicator />
                  <Alert.Content>
                    <Alert.Title>Message sent</Alert.Title>
                    <Alert.Description>Thank you. We'll reply to your email as soon as we can.</Alert.Description>
                  </Alert.Content>
                </Alert.Root>
              )}
              {status.kind === "error" && (
                <Alert.Root status="error" variant="subtle">
                  <Alert.Indicator />
                  <Alert.Content>
                    <Alert.Title>Your message wasn't sent</Alert.Title>
                    <Alert.Description>
                      {status.message}
                      {site.contactEmail && (
                        <>
                          {" "}
                          You can also email{" "}
                          <Link href={`mailto:${site.contactEmail}`} textDecoration="underline">
                            {site.contactEmail}
                          </Link>
                          .
                        </>
                      )}
                    </Alert.Description>
                  </Alert.Content>
                </Alert.Root>
              )}

              <Button type="submit" colorPalette="brass" size="lg" alignSelf={{ base: "stretch", md: "flex-start" }} loading={status.kind === "sending"} loadingText="Sending">
                <LuSend /> Send message
              </Button>
              <Text id="contact-note" fontSize="xs" color="fg.subtle">
                This form isn&apos;t monitored around the clock. For anything urgent, please contact the MindScape 3D team
                directly{site.contactEmail ? ` at ${site.contactEmail}` : ""}.
              </Text>
            </Stack>
          </chakra.form>
        </Card.Body>
      </Card.Root>
    </Section>
  )
}
