export const topics = ["General question", "Help with the game", "Report a bug", "Feedback", "School or research inquiry", "Press"] as const

// Screenshots can be attached to bug reports. They are shrunk in the browser first (longest side, JPEG quality),
// because a Vercel function accepts at most 4.5 MB per request.
export const BUG_TOPIC = "Report a bug"
export const MAX_SHOTS = 3
export const SHOT_MAX_SIDE = 1600
export const SHOT_MAX_BYTES = 1_200_000 // per screenshot after shrinking
export const SHOT_TYPES = ["image/png", "image/jpeg", "image/webp"]
