import type { Metadata } from "next"
import { NpcMaker } from "@/components/npc-maker"

export const metadata: Metadata = {
  title: "NPC Maker",
  description: "Build a simple animated low-poly NPC and export it for Unity.",
  alternates: { canonical: "/npc-maker" },
}

export default function NpcMakerPage() {
  return <NpcMaker />
}
