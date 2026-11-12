import { createSystem, defaultConfig, defineConfig } from "@chakra-ui/react"

// The game's own palette (Assets/UI Toolkit/MainMenuNew/MainMenuNew.uss and the story screens):
// ink and wood for the dark panels, paper and cream for the light ones, brass and gold for edges and highlights,
// and the night-teal veil behind the story screens. The site is always dark (the game's look); only the _dark values are used.
const config = defineConfig({
  globalCss: {
    html: { scrollBehavior: "smooth", scrollPaddingTop: "80px" },
    body: { bg: "bg", color: "fg" },
    "::selection": { bg: "brass.solid", color: "brass.contrast" },
  },
  theme: {
    // Hero animations (AnimatedLogo, Fireflies, the slow zoom on the hero picture).
    keyframes: {
      "ms-logo-in": {
        from: { opacity: 0, transform: "translateY(24px) scale(0.94)", filter: "blur(6px)" },
        to: { opacity: 1, transform: "translateY(0) scale(1)", filter: "blur(0)" },
      },
      "ms-float": { "0%, 100%": { transform: "translateY(0)" }, "50%": { transform: "translateY(-8px)" } },
      "ms-breathe": {
        "0%, 100%": { opacity: 0.35, transform: "translateX(-50%) scale(0.85)" },
        "50%": { opacity: 1, transform: "translateX(-50%) scale(1.15)" },
      },
      "ms-glow": {
        "0%, 100%": { filter: "drop-shadow(0 0 6px rgba(216,180,108,0.25))" },
        "50%": { filter: "drop-shadow(0 0 22px rgba(255,214,140,0.55))" },
      },
      "ms-shimmer": {
        "0%": { backgroundPosition: "150% 0" },
        "35%, 100%": { backgroundPosition: "-50% 0" },
      },
      "ms-firefly": {
        "0%": { opacity: 0, transform: "translate(0, 0)" },
        "15%": { opacity: 0.9 },
        "50%": { transform: "translate(18px, -45vh)" },
        "85%": { opacity: 0.7 },
        "100%": { opacity: 0, transform: "translate(-12px, -90vh)" },
      },
      "ms-wheel": {
        "0%": { opacity: 0, transform: "translateY(0)" },
        "30%": { opacity: 1 },
        "100%": { opacity: 0, transform: "translateY(12px)" },
      },
      "ms-chevron": {
        "0%, 100%": { opacity: 0.2, transform: "translateY(-4px)" },
        "50%": { opacity: 1, transform: "translateY(4px)" },
      },
      "ms-kenburns": { from: { transform: "scale(1)" }, to: { transform: "scale(1.08)" } },
    },
    tokens: {
      fonts: {
        heading: { value: "var(--font-story), 'STIX Two Text', Georgia, serif" },
        body: { value: "var(--font-body), 'Comic Neue', 'Trebuchet MS', sans-serif" },
      },
      colors: {
        ink: { value: "#382e25" },
        wood: { value: "#302d28" },
        deepWood: { value: "#211c18" },
        night: { value: "#12181b" },
        paper: { value: "#e3d4b4" },
        paperLight: { value: "#efe4cd" },
        cream: { value: "#f0e4cc" },
        brass: {
          50: { value: "#fbf6ea" },
          100: { value: "#f3e7c9" },
          200: { value: "#e8d4a4" },
          300: { value: "#ddc184" },
          400: { value: "#d8b46c" },
          500: { value: "#bda477" },
          600: { value: "#a08a64" },
          700: { value: "#80623c" },
          800: { value: "#594a36" },
          900: { value: "#382e25" },
          950: { value: "#211c18" },
        },
        rust: {
          50: { value: "#fbefeb" },
          100: { value: "#f2d5cc" },
          200: { value: "#e3ae9f" },
          300: { value: "#cf8571" },
          400: { value: "#bb6d58" },
          500: { value: "#a35d4b" },
          600: { value: "#8a3f2f" },
          700: { value: "#6d3125" },
          800: { value: "#50241b" },
          900: { value: "#341711" },
          950: { value: "#220e0a" },
        },
      },
    },
    semanticTokens: {
      colors: {
        bg: {
          DEFAULT: { value: { _light: "#f6eedc", _dark: "#12181b" } },
          subtle: { value: { _light: "#efe4cd", _dark: "#171e21" } },
          muted: { value: { _light: "#e3d4b4", _dark: "#1e2427" } },
          emphasized: { value: { _light: "#d5c7ab", _dark: "#2a2622" } },
          panel: { value: { _light: "#fbf6ea", _dark: "#211c18" } },
        },
        fg: {
          DEFAULT: { value: { _light: "#382e25", _dark: "#f0e4cc" } },
          muted: { value: { _light: "#6b5a45", _dark: "#c8b693" } },
          subtle: { value: { _light: "#8a7759", _dark: "#a7916d" } },
        },
        border: {
          DEFAULT: { value: { _light: "#d5c7ab", _dark: "#3a332b" } },
          muted: { value: { _light: "#e3d4b4", _dark: "#2c2823" } },
          emphasized: { value: { _light: "#bda477", _dark: "#79603d" } },
        },
        brass: {
          solid: { value: { _light: "#80623c", _dark: "#d8b46c" } },
          contrast: { value: { _light: "#fbf6ea", _dark: "#211c18" } },
          fg: { value: { _light: "#6d5232", _dark: "#ffe2a0" } },
          muted: { value: { _light: "#e8d4a4", _dark: "#594a36" } },
          subtle: { value: { _light: "#f3e7c9", _dark: "#2a241d" } },
          emphasized: { value: { _light: "#ddc184", _dark: "#79603d" } },
          focusRing: { value: { _light: "#80623c", _dark: "#ffe2a0" } },
          border: { value: { _light: "#bda477", _dark: "#79603d" } },
        },
        rust: {
          solid: { value: { _light: "#8a3f2f", _dark: "#bb6d58" } },
          contrast: { value: { _light: "#fbf6ea", _dark: "#fbf6ea" } },
          fg: { value: { _light: "#8a3f2f", _dark: "#e3ae9f" } },
          muted: { value: { _light: "#f2d5cc", _dark: "#50241b" } },
          subtle: { value: { _light: "#fbefeb", _dark: "#341711" } },
          emphasized: { value: { _light: "#e3ae9f", _dark: "#6d3125" } },
          focusRing: { value: { _light: "#8a3f2f", _dark: "#cf8571" } },
          border: { value: { _light: "#cf8571", _dark: "#6d3125" } },
        },
      },
    },
  },
})

export const system = createSystem(defaultConfig, config)
