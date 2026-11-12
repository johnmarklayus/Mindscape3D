"use client"

import { Alert, Box, Button, Center, Progress, Stack, Text } from "@chakra-ui/react"
import Image from "next/image"
import { useCallback, useEffect, useRef, useState } from "react"
import { LuRotateCcw } from "react-icons/lu"
import { site } from "@/lib/site"

// Runs the Unity WebGL build (Builds/webgl-play, copied to public/game by `npm run sync-game`) on this page.
// The page is only the game: the canvas fills the browser window and loading starts as soon as the page opens.
// The loader settings match the build's own index.html (same company and product name, so saved games carry over).

type UnityInstance = { SetFullscreen: (on: number) => void; Quit: () => Promise<void> }
declare global {
  interface Window {
    createUnityInstance?: (canvas: HTMLCanvasElement, config: Record<string, unknown>, onProgress: (p: number) => void) => Promise<UnityInstance>
  }
}

const BUILD_NAME = "Mindscape"

type State = { phase: "loading"; progress: number } | { phase: "running" } | { phase: "error"; message: string }

export function UnityPlayer() {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const instanceRef = useRef<UnityInstance | null>(null)
  const startedRef = useRef(false)
  const [state, setState] = useState<State>({ phase: "loading", progress: 0 })

  const start = useCallback(() => {
    const canvas = canvasRef.current
    if (!canvas || startedRef.current) return
    startedRef.current = true
    const base = `${site.gameUrl}/Build`
    const config = {
      arguments: [],
      dataUrl: `${base}/${BUILD_NAME}.data.br`,
      frameworkUrl: `${base}/${BUILD_NAME}.framework.js.br`,
      codeUrl: `${base}/${BUILD_NAME}.wasm.br`,
      streamingAssetsUrl: `${site.gameUrl}/StreamingAssets`,
      companyName: "DefaultCompany",
      productName: "mindscape-3d",
      productVersion: site.version,
      showBanner: (msg: string, type: string) => {
        if (type === "error") setState({ phase: "error", message: msg })
      },
    }
    const run = () =>
      window
        .createUnityInstance!(canvas, config, (p) => setState({ phase: "loading", progress: Math.round(p * 100) }))
        .then((instance) => {
          instanceRef.current = instance
          setState({ phase: "running" })
          canvas.focus()
        })
        .catch((err: unknown) => setState({ phase: "error", message: String(err) }))

    if (window.createUnityInstance) return void run()
    const script = document.createElement("script")
    script.src = `${base}/${BUILD_NAME}.loader.js`
    script.async = true
    script.onload = () => void run()
    script.onerror = () =>
      setState({ phase: "error", message: "The game files could not be loaded. Check your connection and try again" })
    document.body.appendChild(script)
  }, [])

  useEffect(() => {
    // No page scrolling behind the game.
    const html = document.documentElement
    const previous = html.style.overflow
    html.style.overflow = "hidden"
    start()
    return () => {
      html.style.overflow = previous
      instanceRef.current?.Quit().catch(() => {})
      instanceRef.current = null
    }
  }, [start])

  return (
    <Box position="fixed" inset="0" bg="#0d1418">
      <canvas
        ref={canvasRef}
        id="unity-canvas"
        tabIndex={-1}
        aria-label="MindScape 3D game"
        style={{ width: "100%", height: "100%", display: "block", background: "#0d1418", outline: "none" }}
      />

      {state.phase !== "running" && (
        <Center position="absolute" inset="0">
          <Image src="/images/hero.jpg" alt="" fill sizes="100vw" priority style={{ objectFit: "cover", opacity: 0.35 }} />
          <Stack position="relative" align="center" gap="5" px="6" textAlign="center" maxW="lg" w="full">
            <Box w={{ base: "240px", md: "380px" }}>
              <Image src="/images/logo.png" alt="MindScape 3D" width={1200} height={450} priority style={{ width: "100%", height: "auto" }} />
            </Box>

            {state.phase === "loading" && (
              <Stack w="full" gap="2" aria-live="polite">
                <Progress.Root value={state.progress} max={100} size="sm" colorPalette="brass" w="full">
                  <Progress.Track bg="rgba(240,228,204,0.15)">
                    <Progress.Range bg="#d8b46c" />
                  </Progress.Track>
                </Progress.Root>
                <Text fontSize="sm" color="#f0e4cc">
                  {state.progress < 90 ? `Loading… ${state.progress}%` : "Getting things ready…"}
                </Text>
                <Text fontSize="xs" color="#c8b693">
                  Take a slow breath while you wait.
                </Text>
              </Stack>
            )}

            {state.phase === "error" && (
              <Stack gap="3" align="center">
                <Alert.Root status="error" variant="solid" rounded="md">
                  <Alert.Indicator />
                  <Alert.Content>
                    <Alert.Title>The game couldn&apos;t start</Alert.Title>
                    <Alert.Description fontSize="sm">
                      {state.message}. Your browser needs WebGL 2; try the latest Chrome or Edge, or download the game.
                    </Alert.Description>
                  </Alert.Content>
                </Alert.Root>
                <Button variant="outline" color="#f0e4cc" borderColor="#bda477" onClick={() => window.location.reload()}>
                  <LuRotateCcw /> Try again
                </Button>
              </Stack>
            )}
          </Stack>
        </Center>
      )}
    </Box>
  )
}
