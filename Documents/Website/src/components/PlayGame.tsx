import { Maximize } from "lucide-react"
import { useEffect, useRef, useState } from "react"
import { Button } from "@/components/ui/button"
import { formatReleaseDate, latestBuild } from "@/data/build"
import { useLanguage, useUiCopy } from "@/lib/language"

const BUILD_DIR = latestBuild.webBuildDir
const BUILD_NAME = latestBuild.webBuildName

interface UnityInstance {
  SetFullscreen(fullscreen: number): void
  Quit(): Promise<void>
}

type CreateUnityInstance = (
  canvas: HTMLCanvasElement,
  config: Record<string, unknown>,
  onProgress?: (progress: number) => void,
) => Promise<UnityInstance>

declare global {
  interface Window {
    createUnityInstance?: CreateUnityInstance
  }
}

function loadLoader(): Promise<CreateUnityInstance> {
  if (window.createUnityInstance) return Promise.resolve(window.createUnityInstance)
  return new Promise((resolve, reject) => {
    const script = document.createElement("script")
    script.src = `${BUILD_DIR}/${BUILD_NAME}.loader.js`
    script.onload = () =>
      window.createUnityInstance ? resolve(window.createUnityInstance) : reject(new Error("Unity loader missing"))
    script.onerror = () => reject(new Error("Failed to load the Unity loader script"))
    document.body.appendChild(script)
  })
}

export function PlayGame() {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const instanceRef = useRef<UnityInstance | null>(null)
  const [progress, setProgress] = useState(0)
  const [ready, setReady] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const { language } = useLanguage()
  const copy = useUiCopy()

  useEffect(() => {
    let cancelled = false
    const canvas = canvasRef.current
    if (!canvas) return

    loadLoader()
      .then((createUnityInstance) =>
        createUnityInstance(
          canvas,
          {
            dataUrl: `${BUILD_DIR}/${BUILD_NAME}.data.br`,
            frameworkUrl: `${BUILD_DIR}/${BUILD_NAME}.framework.js.br`,
            codeUrl: `${BUILD_DIR}/${BUILD_NAME}.wasm.br`,
            streamingAssetsUrl: "StreamingAssets",
            companyName: "DefaultCompany",
            productName: "mindscape-3d",
            productVersion: latestBuild.version,
          },
          (p) => !cancelled && setProgress(p),
        ),
      )
      .then((instance) => {
        if (cancelled) {
          void instance.Quit()
          return
        }
        instanceRef.current = instance
        setReady(true)
      })
      .catch((e: unknown) => !cancelled && setError(e instanceof Error ? e.message : String(e)))

    return () => {
      cancelled = true
      void instanceRef.current?.Quit()
      instanceRef.current = null
    }
  }, [])

  return (
    <div className="flex-1 min-h-0 flex flex-col bg-black">
      <div className="flex items-center gap-2 px-3 h-10 border-b border-border bg-sidebar shrink-0 text-sm">
        <span className="text-muted-foreground truncate">
          Mindscape 3D — {copy.webBuild} {formatReleaseDate(latestBuild.releaseDate, language === "fil" ? "fil-PH" : "en")}
        </span>
        <Button
          variant="ghost"
          size="sm"
          className="ml-auto shrink-0"
          disabled={!ready}
          onClick={() => instanceRef.current?.SetFullscreen(1)}
        >
          <Maximize />
          {copy.fullscreen}
        </Button>
      </div>
      <div className="relative flex-1 min-h-0">
        <canvas ref={canvasRef} id="unity-canvas"className="absolute inset-0 w-full h-full bg-[#231F20]" tabIndex={-1} />
        {!ready && (
          <div className="absolute inset-0 flex flex-col items-center justify-center gap-3 text-sm text-white">
            {error ? (
              <p className="text-red-400 max-w-md text-center px-4">{error}</p>
            ) : (
              <>
                <span>{copy.loading} {Math.round(progress * 100)}%</span>
                <div className="w-48 h-1.5 rounded bg-white/20 overflow-hidden">
                  <div className="h-full bg-white" style={{ width: `${progress * 100}%` }} />
                </div>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
