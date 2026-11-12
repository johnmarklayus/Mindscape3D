import { next } from "@vercel/functions"

// Site-wide password gate (Vercel Routing Middleware). Password lives in the SITE_PASSWORD env var.
const COOKIE = "mindscape_auth"

async function token(password: string) {
  const data = new TextEncoder().encode(`mindscape:${password}`)
  const digest = await crypto.subtle.digest("SHA-256", data)
  return [...new Uint8Array(digest)].map((b) => b.toString(16).padStart(2, "0")).join("")
}

function loginPage(failed: boolean) {
  const html = `<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Mindscape 3D — Password</title>
<style>
body{margin:0;min-height:100vh;display:grid;place-items:center;background:#0b0f19;color:#e5e7eb;font-family:system-ui,sans-serif}
form{display:flex;flex-direction:column;gap:12px;width:min(320px,90vw)}
h1{font-size:20px;margin:0 0 4px}
input,button{padding:10px 12px;border-radius:8px;border:1px solid #2a3142;font-size:15px}
input{background:#111827;color:inherit}
button{background:#34d399;color:#04130d;font-weight:600;border:0;cursor:pointer}
p{margin:0;color:#f87171;font-size:13px}
</style></head><body>
<form method="POST">
<h1>Mindscape 3D</h1>
${failed ? "<p>Incorrect password.</p>" : ""}
<input type="password" name="password" placeholder="Password" autofocus required>
<button type="submit">Enter</button>
</form></body></html>`
  return new Response(html, {
    status: failed ? 401 : 200,
    headers: { "Content-Type": "text/html; charset=utf-8", "Cache-Control": "no-store" },
  })
}

export default async function middleware(request: Request) {
  const password = process.env.SITE_PASSWORD
  if (!password) return new Response("SITE_PASSWORD is not configured", { status: 500 })

  const expected = await token(password)
  const cookies = request.headers.get("cookie") ?? ""
  if (cookies.split(/;\s*/).includes(`${COOKIE}=${expected}`)) return next()

  if (request.method === "POST") {
    const form = await request.formData().catch(() => null)
    if (form?.get("password") === password) {
      return new Response(null, {
        status: 303,
        headers: {
          Location: new URL(request.url).pathname,
          "Set-Cookie": `${COOKIE}=${expected}; Path=/; Max-Age=604800; HttpOnly; Secure; SameSite=Lax`,
        },
      })
    }
    return loginPage(true)
  }
  return loginPage(false)
}

export const config = { matcher: "/((?!favicon.svg).*)" }
