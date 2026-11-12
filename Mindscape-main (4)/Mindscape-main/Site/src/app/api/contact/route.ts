import { NextResponse } from "next/server"
import { BUG_TOPIC, MAX_SHOTS, SHOT_MAX_BYTES, SHOT_TYPES, topics } from "@/lib/contact"

// Contact form endpoint. Checks the message, then e-mails it to CONTACT_TO_EMAIL through Resend's HTTP API
// (RESEND_API_KEY, CONTACT_FROM_EMAIL on a domain verified in Resend). Nothing is stored on the site itself.
// Bug reports may carry up to three screenshots, attached to the email.

export const runtime = "nodejs"

const recent = new Map<string, number[]>() // ip -> send times, a light per-instance rate limit
const LIMIT = 5
const WINDOW_MS = 10 * 60 * 1000

function tooMany(ip: string) {
  const now = Date.now()
  const times = (recent.get(ip) ?? []).filter((t) => now - t < WINDOW_MS)
  times.push(now)
  recent.set(ip, times)
  return times.length > LIMIT
}

const escape = (s: string) => s.replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]!)

export async function POST(request: Request) {
  let body: Record<string, unknown> = {}
  let files: File[] = []
  try {
    if ((request.headers.get("content-type") ?? "").includes("multipart/form-data")) {
      const form = await request.formData()
      for (const [key, value] of form.entries()) {
        if (key === "screenshots" && typeof value !== "string") files.push(value)
        else if (typeof value === "string") body[key] = value
      }
    } else {
      body = await request.json()
    }
  } catch {
    return NextResponse.json({ error: "The form could not be read. Please try again." }, { status: 400 })
  }

  const str = (k: string, max: number) => (typeof body[k] === "string" ? (body[k] as string).trim().slice(0, max) : "")
  const name = str("name", 100)
  const email = str("email", 200)
  const message = str("message", 4000)
  const topic = (topics as readonly string[]).includes(str("topic", 60)) ? str("topic", 60) : topics[0]

  // A filled hidden field means a bot: answer as if it worked, send nothing.
  if (str("website", 200)) return NextResponse.json({ ok: true })

  if (!name || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email) || message.length < 10 || body.agree !== "on") {
    return NextResponse.json({ error: "Please fill in your name, a valid email and a message, and tick the agreement." }, { status: 422 })
  }

  if (topic !== BUG_TOPIC) files = []
  if (files.length > MAX_SHOTS) {
    return NextResponse.json({ error: `Please attach at most ${MAX_SHOTS} screenshots.` }, { status: 422 })
  }
  if (files.some((f) => !SHOT_TYPES.includes(f.type) || f.size > SHOT_MAX_BYTES * 1.5)) {
    return NextResponse.json({ error: "Screenshots must be PNG, JPG or WebP images of a reasonable size." }, { status: 422 })
  }
  const attachments = await Promise.all(
    files.map(async (f, i) => ({
      filename: `screenshot-${i + 1}.${f.type.split("/")[1].replace("jpeg", "jpg")}`,
      content: Buffer.from(await f.arrayBuffer()).toString("base64"),
    })),
  )

  const ip = request.headers.get("x-forwarded-for")?.split(",")[0]?.trim() || "unknown"
  if (tooMany(ip)) {
    return NextResponse.json({ error: "Too many messages from your connection. Please wait a few minutes." }, { status: 429 })
  }

  const key = process.env.RESEND_API_KEY
  const to = process.env.CONTACT_TO_EMAIL
  const from = process.env.CONTACT_FROM_EMAIL
  if (!key || !to || !from) {
    console.error("contact: RESEND_API_KEY, CONTACT_TO_EMAIL or CONTACT_FROM_EMAIL is not set")
    return NextResponse.json({ error: "The contact form isn't available right now." }, { status: 503 })
  }

  const res = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: { Authorization: `Bearer ${key}`, "Content-Type": "application/json" },
    body: JSON.stringify({
      from,
      to: to.split(",").map((s) => s.trim()),
      reply_to: email,
      subject: `[MindScape 3D] ${topic}: ${name}`,
      text: `From: ${name} <${email}>\nTopic: ${topic}\n\n${message}${attachments.length ? `\n\n(${attachments.length} screenshot(s) attached)` : ""}`,
      html: `<p><b>From:</b> ${escape(name)} &lt;${escape(email)}&gt;<br><b>Topic:</b> ${escape(topic)}</p><p style="white-space:pre-wrap">${escape(message)}</p>`,
      ...(attachments.length ? { attachments } : {}),
    }),
  })

  if (!res.ok) {
    console.error("contact: Resend answered", res.status, await res.text().catch(() => ""))
    return NextResponse.json({ error: "We couldn't send your message right now. Please try again later." }, { status: 502 })
  }
  return NextResponse.json({ ok: true })
}
