import { site } from "@/lib/site"

// The Privacy Policy and Terms and Conditions, shown in the legal modal (legal-modal.tsx).
// Section ids carry the document's name ("privacy-cookies", "terms-license") so a link such as #privacy-cookies
// opens the right document at the right section. Update `updated` when the text changes.

export const legal = {
  privacy: { title: "Privacy Policy", updated: "November 12, 2026" },
  terms: { title: "Terms and Conditions", updated: "November 12, 2026" },
} as const

export function PrivacyContent() {
  return (
    <>
      <p className="lead">
        Your privacy matters, especially in a game about feelings. This policy explains what the MindScape 3D website
          and game collect, why, and the choices you have. We follow the Philippine Data Privacy Act of 2012 (Republic
          Act No. 10173).
      </p>
      <h2 id="privacy-who">Who we are</h2>
      <p>
        MindScape 3D is a capstone project made by a student team of {site.institution} (&quot;we&quot;, &quot;us&quot;). We are
        responsible for the personal information described here. You can reach us through the{" "}
        <a href="/#contact">contact form</a>.
      </p>

      <h2 id="privacy-website">What the website collects</h2>
      <h3 id="privacy-contact-form">Contact form</h3>
      <p>
        When you send a message we receive your name, email address, the topic you chose and your message. We use them
        only to read and answer you. The message is delivered to the team&apos;s mailbox by our email provider, Resend;
        the website itself does not store it. We keep messages for as long as we need to answer and follow up, and no
        longer than one year.
      </p>
      <h3 id="privacy-cookies">Cookies and similar storage</h3>
      <ul>
        <li>
          <strong>Strictly necessary:</strong> your cookie choice (a first-party cookie and browser storage named
          &quot;mindscape-consent&quot;, kept for 180 days). This is always on.
        </li>
        <li>
          <strong>Analytics (optional):</strong> only if you allow it, Vercel Web Analytics counts page views, the page
          you came from, your country and device type. It does not use cookies that identify you and does not follow you
          across other sites. You can turn it off at any time with &quot;Cookie settings&quot; at the bottom of every page.
        </li>
      </ul>
      <p>We do not use advertising or social-media tracking.</p>
      <h3 id="privacy-logs">Server logs</h3>
      <p>
        Our hosting provider, Vercel, processes technical data such as IP addresses to deliver pages, keep the site
        secure and prevent abuse. These logs are short-lived and not used to identify you.
      </p>

      <h2 id="privacy-game">What the game collects</h2>
      <h3>Playing without an account</h3>
      <p>
        Your progress, story choices, settings, reflection journal and self-assessments are saved only on your device
        (or, in the web version, in your browser&apos;s storage). They are not sent to us. Uninstalling the game or
        clearing your browser data removes them.
      </p>
      <h3>Playing with an account (optional)</h3>
      <p>If you create an account to keep your progress across devices, we store:</p>
      <ul>
        <li>your username and email address (to sign you in and send verification and recovery codes);</li>
        <li>your password, kept only in hashed form by our authentication provider, so nobody can read it;</li>
        <li>if you choose &quot;Continue with Google&quot;, the email address Google shares with us;</li>
        <li>your episode progress, reflection journal entries and self-assessment answers.</li>
      </ul>
      <p>
        Accounts and game data are stored with Supabase, our database provider. Verification emails are sent through
        Resend. Journal entries and self-assessments can describe how you feel, so we treat them as sensitive: they are
        only reachable through your signed-in account and are never sold, shared for advertising or used to judge you.
      </p>

      <h2 id="privacy-use">How we use information</h2>
      <ul>
        <li>to run the game and your account, and to keep your progress in sync;</li>
        <li>to answer messages and support requests;</li>
        <li>to understand, in aggregate, how the website is used so we can improve it (only with your consent);</li>
        <li>for the academic evaluation of the project, using only anonymous, aggregated results, never your name or entries.</li>
      </ul>

      <h2 id="privacy-sharing">Who we share it with</h2>
      <p>
        Only the service providers that help us run MindScape 3D: Vercel (website hosting and optional analytics),
        Supabase (accounts and game data), Resend (email) and Google (only if you sign in with Google). They process
        data on our behalf and may store it outside the Philippines with appropriate safeguards. We do not sell personal
        information. We may disclose information if the law requires it.
      </p>

      <h2 id="privacy-retention">How long we keep it</h2>
      <p>
        Account data is kept while your account is active. When you delete your account in the game (Options &gt;
        Account), it is closed immediately and kept in an archive for 30 days, during which you can recover it. After 30
        days it is scheduled for permanent deletion. Data saved only on your device stays there until you remove it.
      </p>

      <h2 id="privacy-rights">Your rights</h2>
      <p>
        Under the Data Privacy Act you may ask to be informed about, access, correct, delete or obtain a copy of your
        personal information, object to its processing, and withdraw consent at any time. You can delete your account
        from inside the game, or <a href="/#contact">contact us</a> for any other request. You may also
        complain to the National Privacy Commission (privacy.gov.ph).
      </p>

      <h2 id="privacy-security">Security</h2>
      <p>
        Connections to the website and our providers are encrypted, passwords are hashed, and game data can only be read
        through your signed-in account. No system is perfectly secure, so please use a strong, unique password.
      </p>

      <h2 id="privacy-age">Who the game is for</h2>
      <p>
        MindScape 3D is made for young adults. If you are under 18, please use the game and create an account only with
        the permission of a parent or guardian.
      </p>

      <h2 id="privacy-health">A note on wellbeing</h2>
      <p>
        MindScape 3D is an awareness and learning tool. It does not diagnose or treat any condition, and we do not
        monitor journal entries for emergencies. If you need help now, call the NCMH Crisis Hotline at 1553.
      </p>

      <h2 id="privacy-changes">Changes to this policy</h2>
      <p>
        We will update this page if our practices change and show the new date at the top. For important changes we
        will also tell players in the game or on the home page.
      </p>
    </>
  )
}

export function TermsContent() {
  return (
    <>
      <p className="lead">
        These terms apply when you visit this website, play MindScape 3D in your browser, download it, or create an
          account. By doing any of these you agree to them. If you do not agree, please do not use the game or the site.
      </p>
      <h2 id="terms-about">1. About MindScape 3D</h2>
      <p>
        MindScape 3D is a free educational game made as a capstone project by students of {site.institution}. It is
        offered for personal, non-commercial use to raise awareness of stress and to practise coping skills.
      </p>

      <h2 id="terms-health">2. Not medical advice</h2>
      <p>
        The game, its exercises and this website are for information and learning only. They are{" "}
        <strong>not a substitute for professional medical or psychological advice, diagnosis or treatment</strong>, and
        they are not a crisis service. If you are in distress or danger, contact a professional, a trusted person, the
        NCMH Crisis Hotline (1553) or your local emergency number.
      </p>

      <h2 id="terms-license">3. Your licence to use the game</h2>
      <p>
        We give you a personal, non-exclusive, non-transferable, revocable licence to download, install and play MindScape
        3D for free on devices you own or control. You may not:
      </p>
      <ul>
        <li>sell, rent, or charge for the game or any part of it;</li>
        <li>modify, decompile or redistribute the game files, except as the law allows;</li>
        <li>reuse its art, models, story, music or code in other works without our written permission;</li>
        <li>use the game or the site to break the law or to harm others.</li>
      </ul>

      <h2 id="terms-accounts">4. Accounts</h2>
      <p>
        An account is optional. If you create one, give accurate information, keep your password private, and tell us
        if you think someone else has used your account. You can delete your account at any time from the game&apos;s
        options; see the <a href="#privacy-retention">Privacy Policy</a> for what happens next. We may
        suspend accounts that are used to abuse the service.
      </p>

      <h2 id="terms-content">5. What you write</h2>
      <p>
        Your journal entries and answers belong to you. You let us store and process them only to provide the game to
        you, as described in the <a href="#privacy">Privacy Policy</a>. Messages you send through the
        contact form must not contain unlawful or abusive content.
      </p>

      <h2 id="terms-ip">6. Ownership</h2>
      <p>
        The game, including its characters, models, environments, interface, story and the MindScape 3D name and logo,
        belongs to the MindScape 3D team. Third-party tools and services keep their own licences.
      </p>

      <h2 id="terms-availability">7. Availability and changes</h2>
      <p>
        We provide the game and site &quot;as is&quot; and &quot;as available&quot;. As a student project, features, downloads and
        online services may change, pause or end, and we do not promise they will always be error-free. Check the system
        requirements before you download.
      </p>

      <h2 id="terms-liability">8. Limitation of liability</h2>
      <p>
        To the extent the law allows, the MindScape 3D team and {site.institution} are not liable for indirect or
        consequential losses, lost data, or damage to devices arising from using or being unable to use the game or the
        site. Nothing in these terms limits liability that cannot be limited by law.
      </p>

      <h2 id="terms-links">9. Other websites</h2>
      <p>
        Links to hotlines and other organisations are provided for convenience. We are not responsible for their content
        or availability.
      </p>

      <h2 id="terms-law">10. Governing law</h2>
      <p>These terms are governed by the laws of the Republic of the Philippines.</p>

      <h2 id="terms-changes">11. Changes to these terms</h2>
      <p>
        We may update these terms and will show the new date at the top of this page. Continuing to use the game or the
        site after a change means you accept the updated terms.
      </p>

      <h2 id="terms-contact">12. Contact</h2>
      <p>
        Questions about these terms? <a href="/#contact">Send us a message</a>.
      </p>
    </>
  )
}
