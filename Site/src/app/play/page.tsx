import type { Metadata } from "next"
import { UnityPlayer } from "@/components/unity-player"
import { site } from "@/lib/site"

export const metadata: Metadata = {
  title: "Play in your browser",
  description:
    "Play MindScape 3D free in your web browser, with nothing to install. Explore, make choices and practise calming skills as Joey.",
  alternates: { canonical: "/play" },
  openGraph: { url: "/play", title: `Play ${site.name} in your browser` },
}

// Only the game: it fills the whole browser window and starts loading right away.
export default function PlayPage() {
  return (
    <main>
      <h1 style={{ position: "absolute", width: 1, height: 1, overflow: "hidden", clip: "rect(0 0 0 0)" }}>{site.name}</h1>
      <UnityPlayer />
    </main>
  )
}
