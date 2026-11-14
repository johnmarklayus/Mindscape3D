---
id: accounts
group: Saves & Accounts
nav: Saves and online accounts
---

# Saves and Online Accounts

How progress is saved on the device and, with an account, in the cloud (Supabase).

**Offline:** progress, choices and the journal are saved on the device, separately for each profile. Players can delete saves from the menu.

**Online (optional):** `Assets/Scripts/Data/MindscapeCloud.cs` talks to a Supabase project:

- **Database**: tables for players, progress, journal entries, assessments and episode records. The tables are closed to the public key, so the game reads and writes only through RPC functions.
- **Edge function `account`**: sign-up with an email code (OTP), sign-in, Google sign-in hand-off, a 30-day account archive (delete) and recovery. Only Gmail and Yahoo addresses are accepted, each email only once, with a strong password.

## Set up a new Supabase project

```bash
supabase login
supabase link --project-ref <your-project-ref>
supabase db push                       # runs supabase/migrations in order
supabase functions deploy account
supabase secrets set RESEND_API_KEY=... MAIL_FROM="Mindscape <no-reply@your-domain>"
```

`SUPABASE_URL`, `SUPABASE_ANON_KEY` and `SUPABASE_SERVICE_ROLE_KEY` are provided to the function automatically. Then put the new project URL and publishable key in `MindscapeCloud.cs`. **Never put the service-role key in the game.**

More: [Supabase Setup](/#workflow-supabase) · [Add a Supabase Table](/#workflow-supabase-data) · [Accounts, Progress & Saves](/#system-accounts)
