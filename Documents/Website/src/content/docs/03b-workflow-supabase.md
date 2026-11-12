---
id: workflow-supabase
group: Workflows
nav: Supabase Setup
---

# Supabase Connection Setup and Settings

Supabase is optional: a player can choose **Play offline**, in which case Mindscape saves on the device. Online accounts, cloud progress, journal entries and assessments require a hosted Supabase project configured as described below.

This project uses:

- Supabase Auth for email/password, emailed one-time codes and Google sign-in;
- the `account` Edge Function as the only account gateway used by the game;
- PostgreSQL RPC functions for player data; and
- row-level security with direct table access closed to game clients.

The Unity connection is in `Assets/Scripts/Data/MindscapeCloud.cs`. The server source is in `supabase/functions/account/index.ts`, and the database schema is reproduced from `supabase/migrations/`.

After this connection works, use [Add a Supabase Table and Use It in Unity](#workflow-supabase-data) for a complete copy-paste table, secure RPC, `MindscapeCloud` integration and test UI.

## What you need

- A Supabase organization and hosted project
- The project's **Project ref** and **Publishable key**
- The [Supabase CLI](https://supabase.com/docs/guides/local-development/cli/getting-started)
- A custom SMTP provider before production email sign-up
- Optional: a Google Cloud OAuth client for **Continue with Google**
- Optional: a Resend API key for the separate account-deletion notification

> [!WARN] Client-safe key only
>
> Put only the Supabase **publishable** key in the Unity project. Never put a secret key, legacy `service_role` key, database password, Google client secret, SMTP password or Resend key in Unity, git, documentation, screenshots or a player build.

## 1. Create the Supabase project

1. Create a project in the [Supabase dashboard](https://supabase.com/dashboard).
2. Open **Project Settings ▸ General** and copy the **Reference ID** (the project ref).
3. Open **Project Settings ▸ API Keys** and copy the client-safe **Publishable key**. Do not copy a secret or `service_role` key.
4. Keep the database password in a password manager. The game does not need it.

The resulting endpoints follow this pattern:

```text
RPC:      https://<PROJECT_REF>.supabase.co/rest/v1/rpc/
Account:  https://<PROJECT_REF>.supabase.co/functions/v1/account
```

## 2. Link the repository and apply the schema

Run these commands from the repository root. If `supabase/config.toml` does not exist yet, initialize the CLI metadata first:

```sh
supabase login
supabase init
supabase link --project-ref <PROJECT_REF>
supabase migration list --remote
supabase db push --dry-run --remote
supabase db push --remote
```

`db push --dry-run --remote` shows the pending migrations without applying them. The real push creates or updates:

| Database object | Purpose |
| --- | --- |
| `players` | Username, Auth user link and active/archived status |
| `episode_progress` | Started/completed episode state |
| `journal_entries` | Player reflection journal |
| `assessments` | Stress/overwhelm check-ins |
| `episode_records` | Episode result and timing history |
| `google_handoffs` | Short-lived server-side state for cross-platform Google sign-in |
| Public RPC functions | Authenticated reads/writes used by `MindscapeCloud` |
| `mindscape-purge-archived-accounts` cron job | Permanently removes accounts after the 30-day recovery period |

Do not manually recreate these tables in Table Editor. Add future schema changes as a new migration and apply them with the same dry-run/push workflow.

> [!WARN] Remote reset is destructive
>
> Do not run `supabase db reset --remote` on a project with player data. It rebuilds the remote database from migrations and can destroy production data.

## 3. Deploy the account Edge Function

Deploy the function to the linked hosted project:

```sh
supabase functions deploy account --no-verify-jwt
```

`--no-verify-jwt` is intentional. Sign-up, recovery and Google callback requests do not start with a player JWT; `account/index.ts` validates each action and token itself. Supabase automatically provides `SUPABASE_URL`, `SUPABASE_ANON_KEY` and `SUPABASE_SERVICE_ROLE_KEY` to the hosted function. Do not duplicate those values as custom secrets.

After any change to `supabase/functions/account/index.ts`, deploy the function again. Use **Edge Functions ▸ account ▸ Logs** in the dashboard to diagnose server errors.

### Optional deletion email

Supabase Auth SMTP sends sign-up and password-recovery codes. The deletion notice is separate and uses the Resend API directly. Configure it only if that notice is required:

```sh
supabase secrets set RESEND_API_KEY=<RESEND_API_KEY> MAIL_FROM="Mindscape <no-reply@yourdomain.com>"
```

The sender domain must be verified with Resend. If these secrets are absent, account archive/recovery still works; only the deletion notification is skipped.

## 4. Configure email authentication

In the Supabase dashboard:

1. Open **Authentication ▸ Sign In / Providers ▸ Email**. Enable the Email provider and turn **Confirm email** on.
2. Open **Authentication ▸ Email Templates**.
3. Edit **Confirm signup** and **Reset password** so the message visibly contains `{{ .Token }}`. The game asks the player to type that six-digit OTP; it does not consume an email link.
4. Open **Authentication ▸ SMTP Settings** and configure a production SMTP provider.
5. Review **Authentication ▸ Rate Limits** after SMTP is connected. Choose limits appropriate for expected sign-up, resend and password-reset traffic.

The default Supabase sender is for development only: it sends only to project-team addresses and is heavily rate-limited. Test with a team-member address until custom SMTP is ready.

Recommended SMTP settings:

- Use a verified sending domain and a dedicated address such as `no-reply@auth.example.com`.
- Configure SPF, DKIM and DMARC with the mail provider.
- Keep authentication mail separate from marketing mail.
- Disable link tracking for auth email if the provider offers it; Mindscape uses the OTP token.

## 5. Configure Google sign-in

Skip this section if the **Continue with Google** button will not be used.

### Google Cloud

1. In Google Cloud Console, configure the OAuth consent screen.
2. Create an **OAuth client ID** with application type **Web application**.
3. Add this Supabase callback as an **Authorized redirect URI**:

   ```text
   https://<PROJECT_REF>.supabase.co/auth/v1/callback
   ```

4. Copy the Google client ID and client secret.

### Supabase

1. Open **Authentication ▸ Sign In / Providers ▸ Google**.
2. Enable Google and paste the Google client ID and client secret.
3. Open **Authentication ▸ URL Configuration**.
4. Add this exact wildcard to **Redirect URLs**:

   ```text
   https://<PROJECT_REF>.supabase.co/functions/v1/account/google/done/**
   ```

5. Set **Site URL** to a real project website or landing page. Mindscape supplies its Edge Function callback explicitly, but the Site URL remains Supabase's fallback redirect.

The game opens the browser, the Edge Function performs a PKCE exchange, and the game polls for the result. No Android deep link or desktop custom URI scheme is required. A first-time Google player is asked to choose a unique username.

> [!TIP] Two different callback settings
>
> Google Cloud must allow Supabase Auth's `/auth/v1/callback`. Supabase Auth must separately allow the Edge Function's `/functions/v1/account/google/done/**` redirect. Google sign-in fails if either entry is missing or belongs to a different project ref.

## 6. Connect the Unity game

Open `Assets/Scripts/Data/MindscapeCloud.cs` and replace only these constants:

```csharp
const string RpcUrl = "https://<PROJECT_REF>.supabase.co/rest/v1/rpc/";
const string AccountUrl = "https://<PROJECT_REF>.supabase.co/functions/v1/account";
const string PublishableKey = "sb_publishable_...";
```

Keep the trailing slash on `RpcUrl`; RPC method names are appended to it. `AccountUrl` has no trailing slash. Save the file and wait for Unity to compile before testing.

For separate development and production projects, use separate builds or an environment-specific configuration asset. Never point a development build at production while testing migrations, deletion or recovery.

## 7. Verify the complete connection

Test from `Assets/Scenes/Intro.unity` so the same account UI used by builds is exercised:

1. Register with a new email and confirm the six-digit code arrives.
2. Enter the code and confirm the main menu shows the signed-in username.
3. Log out and log back in once by username and once by email.
4. Complete an episode, add a journal entry and submit a stress check-in.
5. Confirm rows appear in `players`, `episode_progress`, `journal_entries`, `assessments` and `episode_records`.
6. Restart the game and confirm the session refreshes and progress downloads.
7. Test **Forgot password?** through code verification and password replacement.
8. If enabled, test Google sign-in in the Editor and in at least one real target build.
9. Test **Play offline** with the network unavailable; the story must still save locally.

Use these server-side checks when something fails:

```sh
supabase migration list --remote
supabase functions list
supabase secrets list
```

The secrets command lists names, not plaintext values. In the dashboard, inspect **Authentication ▸ Users**, **Edge Function logs**, **Postgres logs** and **Table Editor**. Avoid logging access tokens, refresh tokens, passwords or OTP codes.

## Required settings checklist

| Setting | Required value |
| --- | --- |
| Unity `RpcUrl` | Current project ref, `/rest/v1/rpc/`, trailing slash |
| Unity `AccountUrl` | Current project ref, `/functions/v1/account` |
| Unity key | Publishable key only |
| Database | Every migration applied in timestamp order |
| Edge Function | `account` deployed with `--no-verify-jwt` |
| Email provider | Enabled |
| Confirm email | On |
| Confirm signup template | Contains `{{ .Token }}` |
| Reset password template | Contains `{{ .Token }}` |
| Production SMTP | Configured and verified |
| Google provider | Enabled only when Google sign-in is offered |
| Google Cloud redirect | `https://<PROJECT_REF>.supabase.co/auth/v1/callback` |
| Supabase redirect allow list | `https://<PROJECT_REF>.supabase.co/functions/v1/account/google/done/**` |
| Resend secrets | Optional; deletion-notification email only |

## Troubleshooting

| Symptom | Check |
| --- | --- |
| `401` from the account function | Correct publishable key, correct project ref, function deployed with `--no-verify-jwt` |
| Function returns `404` | `AccountUrl` and deployed function name are both `account` |
| RPC returns `404` | All migrations were applied to the same project used by `RpcUrl` |
| Sign-up email never arrives | Confirm Email provider, team-address restriction on default SMTP, custom SMTP credentials and Auth logs |
| Code is rejected | Template uses `{{ .Token }}`, the newest code is entered, and it has not expired |
| Google reports a redirect mismatch | Google Cloud Supabase callback URI and Supabase Edge Function redirect allow-list entry |
| Google browser succeeds but game keeps waiting | `google_handoffs` migration applied, same project ref in Unity/function/provider, Edge Function logs |
| Username/email already used unexpectedly | Check `players` and Supabase Auth users; the unique-email migration intentionally prevents duplicates |
| Deleted account cannot recover | Recovery is within 30 days, email still exists in Auth, archive migration and cron job are installed |
| Cloud data is empty after login | Player is signed in, `ensure_profile` succeeded, data RPC migration exists, and Edge/Postgres logs show no RLS or permission error |
| Offline play stopped working | This is a client-side regression; Supabase availability must never be required for **Play offline** |

Official references: [CLI workflow](https://supabase.com/docs/guides/local-development/cli-workflows), [Google sign-in](https://supabase.com/docs/guides/auth/social-sign-in/auth-google), [redirect URLs](https://supabase.com/docs/guides/auth/redirect-urls), [email templates](https://supabase.com/docs/guides/auth/auth-email-templates), and [custom SMTP](https://supabase.com/docs/guides/auth/auth-smtp).
