// Update these when you publish a new build.
// apkUrl: leave "" to hide the Download APK button. Vercel cannot host files over 100 MB, and the 2026-11-06 APK is 193 MB, so
// it has to be hosted elsewhere (put its full https URL here).
export const latestBuild = {
  version: "0.3.0",
  releaseDate: "2026-11-06",
  apkUrl: "",
  apkSize: "193 MB",
  webBuildDir: "./game-builds/2026-11-06/Build",
  webBuildName: "WebGL",
}

export function formatReleaseDate(iso: string, locale?: string) {
  return new Date(`${iso}T00:00:00`).toLocaleDateString(locale, {
    year: "numeric",
    month: "short",
    day: "numeric",
  })
}
