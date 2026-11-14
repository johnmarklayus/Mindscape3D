import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { OnboardingPage } from './components/OnboardingPage.tsx'
import { ThemeProvider } from './lib/theme.tsx'
import { LanguageProvider } from './lib/language.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ThemeProvider>
      <LanguageProvider>
        {/* /onboarding is its own page; everything else is the hash-routed docs. */}
        {window.location.pathname.replace(/\/+$/, '') === '/onboarding' ? <OnboardingPage /> : <App />}
      </LanguageProvider>
    </ThemeProvider>
  </StrictMode>,
)
