import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from "react"

export type Language = "en" | "fil"

const STORAGE_KEY = "mindscape-docs-language"

interface LanguageContextValue {
  language: Language
  setLanguage: (language: Language) => void
}

const LanguageContext = createContext<LanguageContextValue | null>(null)

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [language, setLanguage] = useState<Language>(() => {
    const saved = localStorage.getItem(STORAGE_KEY)
    return saved === "fil" ? "fil" : "en"
  })

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, language)
    document.documentElement.lang = language === "fil" ? "fil" : "en"
  }, [language])

  const value = useMemo(() => ({ language, setLanguage }), [language])
  return <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>
}

export function useLanguage() {
  const context = useContext(LanguageContext)
  if (!context) throw new Error("useLanguage must be used inside LanguageProvider")
  return context
}

export const uiCopy = {
  en: {
    docsTitle: "Mindscape 3D Docs",
    projectDocs: "Project & workflow documentation",
    filterTopics: "Filter topics…",
    openNavigation: "Open navigation",
    collapseNavigation: "Collapse navigation",
    expandNavigation: "Expand navigation",
    released: "Released",
    downloadApk: "Download APK",
    playGame: "Play Game (Web)",
    onboarding: "Onboarding",
    onboardingTitle: "Onboarding: From Scratch to Deployment",
    backToDocs: "Back to docs",
    onThisPage: "On this page",
    previous: "Previous",
    next: "Next",
    filterOnboarding: "Filter onboarding…",
    playGameTitle: "Play Game",
    scripts: "Scripts",
    scriptsGroup: "Scripts (Line by Line)",
    overview: "Overview",
    menuItem: "Menu Item",
    loadingEditor: "Loading editor…",
    loading: "Loading…",
    notes: "notes",
    explanations: "Explanations",
    noNotes: "No annotated lines match this file.",
    noteHelp: "Click a highlighted line in the code, or a note below, to jump between them.",
    line: "Line",
    lines: "Lines",
    staleNotes: "note(s) point at code that no longer exists in this file.",
    scriptsTitle: "Scripts, Line by Line",
    scriptsIntro:
      "Pick a script to open it, read-only, next to an explanation of the lines worth explaining. This covers the core gameplay scripts; MainMenuController.cs and the Cutscene*.cs family aren't annotated yet — add a src/content/scripts/<id>.json file and list its id in index.json to cover them (npm run sync copies the code in).",
    webBuild: "Web build",
    fullscreen: "Fullscreen",
  },
  fil: {
    docsTitle: "Mindscape 3D Docs",
    projectDocs: "Gabay sa project at mga workflow",
    filterTopics: "Maghanap ng topic…",
    openNavigation: "Buksan ang navigation",
    collapseNavigation: "Itago ang navigation",
    expandNavigation: "Ipakita ang navigation",
    released: "Inilabas",
    downloadApk: "I-download ang APK",
    playGame: "Laruin sa Web",
    onboarding: "Onboarding",
    onboardingTitle: "Onboarding: Mula Simula Hanggang Deployment",
    backToDocs: "Bumalik sa docs",
    onThisPage: "Sa page na ito",
    previous: "Nakaraan",
    next: "Susunod",
    filterOnboarding: "Hanapin sa onboarding…",
    playGameTitle: "Laruin ang Game",
    scripts: "Mga Script",
    scriptsGroup: "Mga Script (Line by Line)",
    overview: "Pangkalahatang Gabay",
    menuItem: "Menu Item",
    loadingEditor: "Nilo-load ang editor…",
    loading: "Nilo-load…",
    notes: "paliwanag",
    explanations: "Mga Paliwanag",
    noNotes: "Walang annotated line na tumutugma sa file na ito.",
    noteHelp: "I-click ang highlighted line sa code o ang note sa ibaba para lumipat sa pagitan ng mga ito.",
    line: "Line",
    lines: "Lines",
    staleNotes: "note ang nakaturo sa code na wala na sa file na ito.",
    scriptsTitle: "Mga Script, Line by Line",
    scriptsIntro:
      "Pumili ng script para buksan ito bilang read-only, katabi ng paliwanag sa mahahalagang line. Sakop nito ang core gameplay scripts; hindi pa annotated ang MainMenuController.cs at Cutscene*.cs family. Para idagdag ang mga iyon, gumawa ng src/content/scripts/<id>.json file, ilista ang id nito sa index.json, at gamitin ang npm run sync para kopyahin ang code.",
    webBuild: "Web build",
    fullscreen: "Buong Screen",
  },
} as const

export function useUiCopy() {
  const { language } = useLanguage()
  return uiCopy[language]
}
