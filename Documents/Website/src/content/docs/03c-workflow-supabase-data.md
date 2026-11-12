---
id: workflow-supabase-data
group: Workflows
nav: Add a Supabase Table
---

# Add a Supabase Table and Use It in Unity

This copy-paste example adds **player notes**: each signed-in player can create, edit, list and delete only their own notes. It demonstrates the same secure pattern used by Mindscape's progress and journal tables:

```text
Unity UI → MindscapeCloud → authenticated RPC → player_notes table
```

Unity does not read or write the table directly. The table has RLS enabled and no client table privileges. Three narrowly scoped PostgreSQL functions resolve the current player through `private.player_from_token`, check row ownership and perform the operation.

> [!WARN] Complete the connection setup first
>
> Finish [Supabase Connection Setup and Settings](#workflow-supabase), including all existing migrations, the `account` Edge Function and a working signed-in account. This example depends on the existing `players` table and `private.player_from_token` helper.

## What this example creates

| Piece | Location | Purpose |
| --- | --- | --- |
| Migration | `supabase/migrations/<timestamp>_player_notes.sql` | Table, index, RLS, grants and RPC functions |
| Cloud methods | Inside `Assets/Scripts/Data/MindscapeCloud.cs` | Authenticated save/load/delete calls with token refresh |
| Demo UI | `Assets/Examples/PlayerNotesDemo.cs` | A small screen for testing the feature in Play Mode |

The example is cloud-only. If the feature must work during **Play offline**, add an equivalent local table/PlayerPrefs implementation in `MindscapeDatabase`; see [Add offline support](#supabase-notes-offline) near the end.

## 1. Create the migration

From the repository root, generate a migration:

```sh
supabase migration new player_notes
```

The CLI prints the new file path. Open that `.sql` file and paste everything below:

```sql
-- One player's private notes. Unity never accesses this table directly;
-- it calls the three authenticated RPC functions below.

create table public.player_notes (
  id bigint generated always as identity primary key,
  player_id uuid not null references public.players (id) on delete cascade,
  title text not null check (char_length(title) between 1 and 80),
  body text not null default '' check (char_length(body) <= 1000),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index player_notes_player_updated_idx
  on public.player_notes (player_id, updated_at desc);

-- The table is closed to Data API roles. Access is only through the RPCs.
alter table public.player_notes enable row level security;
revoke all on table public.player_notes from anon, authenticated;
revoke all on sequence public.player_notes_id_seq from anon, authenticated;

-- Create or update a note. p_id <= 0 creates; a positive p_id updates
-- only when that note belongs to the signed-in player.
create function public.save_player_note(
  p_token text,
  p_id bigint,
  p_title text,
  p_body text
)
returns bigint
language plpgsql
security definer
set search_path = ''
as $$
declare
  v_player uuid := private.player_from_token(p_token);
  v_id bigint;
  v_title text := left(btrim(coalesce(p_title, '')), 80);
  v_body text := left(coalesce(p_body, ''), 1000);
begin
  if v_title = '' then
    raise exception 'Enter a note title.' using errcode = '22023';
  end if;

  if coalesce(p_id, 0) <= 0 then
    insert into public.player_notes (player_id, title, body)
    values (v_player, v_title, v_body)
    returning id into v_id;
  else
    update public.player_notes as note
       set title = v_title,
           body = v_body,
           updated_at = now()
     where note.id = p_id
       and note.player_id = v_player
    returning note.id into v_id;

    if v_id is null then
      raise exception 'Note not found.' using errcode = '22023';
    end if;
  end if;

  return v_id;
end;
$$;

-- List only the current player's notes, newest first.
create function public.get_player_notes(p_token text)
returns table (
  id bigint,
  title text,
  body text,
  created_at timestamptz,
  updated_at timestamptz
)
language sql
stable
security definer
set search_path = ''
as $$
  select note.id, note.title, note.body, note.created_at, note.updated_at
    from public.player_notes as note
   where note.player_id = private.player_from_token(p_token)
   order by note.updated_at desc, note.id desc;
$$;

-- Delete only when the note belongs to the current player.
create function public.delete_player_note(p_token text, p_id bigint)
returns boolean
language plpgsql
security definer
set search_path = ''
as $$
declare
  v_count integer;
begin
  delete from public.player_notes as note
   where note.id = p_id
     and note.player_id = private.player_from_token(p_token);
  get diagnostics v_count = row_count;
  return v_count > 0;
end;
$$;

-- SECURITY DEFINER functions are callable by public unless explicitly restricted.
-- Only a signed-in Supabase Auth user may call these three RPCs.
revoke execute on function public.save_player_note(text, bigint, text, text)
  from public, anon;
revoke execute on function public.get_player_notes(text)
  from public, anon;
revoke execute on function public.delete_player_note(text, bigint)
  from public, anon;

grant execute on function public.save_player_note(text, bigint, text, text)
  to authenticated;
grant execute on function public.get_player_notes(text)
  to authenticated;
grant execute on function public.delete_player_note(text, bigint)
  to authenticated;
```

Why this is safe:

- `player_id` is never accepted from Unity. It is derived from the signed-in JWT by the existing helper.
- Every update/delete includes both the note ID and resolved player ID.
- The foreign key uses `on delete cascade`, so permanent account deletion removes the player's notes.
- RLS is enabled and direct `anon`/`authenticated` table grants are removed.
- Each `security definer` function pins `search_path` to empty and schema-qualifies every table.
- Function execution is revoked from signed-out callers and granted only to `authenticated`.

## 2. Preview and apply the migration

Make sure the CLI is linked to the correct project, then preview before changing the remote database:

```sh
supabase migration list --remote
supabase db push --dry-run --remote
supabase db push --remote
```

Confirm in the Supabase dashboard:

1. **Table Editor ▸ player_notes** exists.
2. **Database ▸ Policies ▸ player_notes** shows RLS enabled. No policies are expected because direct table access is revoked.
3. **Database ▸ Functions** contains `save_player_note`, `get_player_notes` and `delete_player_note`.

> [!WARN] Do not use the SQL Editor as the only copy
>
> A dashboard-only table cannot be reproduced for another developer, staging project or disaster recovery. Keep the complete SQL in `supabase/migrations/` and commit it.

## 3. Add the Unity cloud methods

Open `Assets/Scripts/Data/MindscapeCloud.cs`. Inside the `MindscapeCloud` class, paste this block immediately before the existing `// ---------------------------------------------------------------- transport` comment:

```csharp
// ---------------------------------------------------------------- player notes example

static readonly List<PlayerNote> playerNotes = new List<PlayerNote>();

// Read-only view for UI. Only LoadPlayerNotes/SavePlayerNote/DeletePlayerNote
// change this list.
public static IReadOnlyList<PlayerNote> PlayerNotes => playerNotes;

public static async Awaitable<string> LoadPlayerNotes()
{
    if (!IsSignedIn) return "Sign in to load cloud notes.";

    var reply = await Call(
        "get_player_notes",
        JsonUtility.ToJson(new TokenOnly { p_token = Token }));

    if (!reply.ok) return reply.error;

    var parsed = JsonUtility.FromJson<PlayerNoteRows>(Wrap(reply.body));
    playerNotes.Clear();
    if (parsed != null && parsed.items != null)
        playerNotes.AddRange(parsed.items);

    Changed?.Invoke();
    return null;
}

// id <= 0 creates a note; a positive id edits that note.
public static async Awaitable<string> SavePlayerNote(
    long id, string title, string body)
{
    if (!IsSignedIn) return "Sign in to save cloud notes.";

    title = (title ?? "").Trim();
    body = body ?? "";
    if (title.Length == 0) return "Enter a note title.";
    if (title.Length > 80) return "Keep the title to 80 characters.";
    if (body.Length > 1000) return "Keep the note to 1000 characters.";

    var reply = await Call(
        "save_player_note",
        JsonUtility.ToJson(new PlayerNoteCall
        {
            p_token = Token,
            p_id = id,
            p_title = title,
            p_body = body
        }));

    if (!reply.ok) return reply.error;
    return await LoadPlayerNotes();
}

public static async Awaitable<string> DeletePlayerNote(long id)
{
    if (!IsSignedIn) return "Sign in to delete cloud notes.";

    var reply = await Call(
        "delete_player_note",
        JsonUtility.ToJson(new DeletePlayerNoteCall
        {
            p_token = Token,
            p_id = id
        }));

    if (!reply.ok) return reply.error;
    return await LoadPlayerNotes();
}

[Serializable]
public sealed class PlayerNote
{
    public long id;
    public string title;
    public string body;
    public string created_at;
    public string updated_at;
}

[Serializable]
sealed class PlayerNoteRows
{
    public PlayerNote[] items;
}

[Serializable]
sealed class PlayerNoteCall
{
    public string p_token;
    public long p_id;
    public string p_title;
    public string p_body;
}

[Serializable]
sealed class DeletePlayerNoteCall
{
    public string p_token;
    public long p_id;
}
```

This code deliberately uses the existing private `Call(...)` helper. That helper refreshes an expiring access token, retries once after a `401`, attaches the publishable key/JWT and converts server errors into player-safe messages.

### Clear notes when the account changes

Still in `MindscapeCloud.cs`, find `ClearSession()`. It currently clears journal/progress/assessment collections. Add `playerNotes.Clear();` beside those calls:

```csharp
journal.Clear();
progress.Clear();
assessments.Clear();
records.Clear();
playerNotes.Clear();
IsLoaded = false;
```

This is required. Without it, Account B could briefly see Account A's in-memory notes after signing out and switching accounts on the same device.

## 4. Add a copy-paste test screen

Create `Assets/Examples/PlayerNotesDemo.cs` and paste this file:

```csharp
using Mindscape.Data;
using UnityEngine;

// Simple development UI. Replace OnGUI with UI Toolkit for production.
public sealed class PlayerNotesDemo : MonoBehaviour
{
    long editingId;
    string title = "";
    string body = "";
    string status = "";
    bool busy;
    Vector2 scroll;

    async void Start()
    {
        if (MindscapeCloud.IsSignedIn) await Reload();
        else status = "Sign in from the main menu, then press Reload.";
    }

    void OnGUI()
    {
        float width = Mathf.Min(620f, Screen.width - 40f);
        float height = Mathf.Max(200f, Screen.height - 40f);
        GUILayout.BeginArea(new Rect(20f, 20f, width, height), GUI.skin.box);

        GUILayout.Label("SUPABASE PLAYER NOTES");
        GUILayout.Label(MindscapeCloud.IsSignedIn
            ? "Signed in as " + MindscapeCloud.Username
            : "Not signed in");

        GUI.enabled = !busy;
        if (GUILayout.Button("Reload notes")) Reload();

        GUILayout.Space(10f);
        GUILayout.Label(editingId > 0 ? "EDIT NOTE" : "NEW NOTE");
        GUILayout.Label("Title (80 characters maximum)");
        title = GUILayout.TextField(title, 80);
        GUILayout.Label("Body (1000 characters maximum)");
        body = GUILayout.TextArea(body, 1000, GUILayout.Height(90f));

        GUILayout.BeginHorizontal();
        if (GUILayout.Button(editingId > 0 ? "Update" : "Save")) Save();
        if (editingId > 0 && GUILayout.Button("Cancel edit")) ClearEditor();
        GUILayout.EndHorizontal();

        if (!string.IsNullOrEmpty(status)) GUILayout.Label(status);
        GUILayout.Space(10f);

        scroll = GUILayout.BeginScrollView(scroll);
        foreach (var note in MindscapeCloud.PlayerNotes)
        {
            GUILayout.BeginVertical(GUI.skin.box);
            GUILayout.Label(note.title);
            GUILayout.Label(note.body);
            GUILayout.Label("Updated: " + note.updated_at);

            GUILayout.BeginHorizontal();
            if (GUILayout.Button("Edit"))
            {
                editingId = note.id;
                title = note.title;
                body = note.body;
            }
            if (GUILayout.Button("Delete")) Delete(note.id);
            GUILayout.EndHorizontal();
            GUILayout.EndVertical();
        }
        GUILayout.EndScrollView();

        GUI.enabled = true;
        GUILayout.EndArea();
    }

    async void Reload()
    {
        busy = true;
        status = "Loading...";
        string error = await MindscapeCloud.LoadPlayerNotes();
        status = error ?? "Loaded " + MindscapeCloud.PlayerNotes.Count + " note(s).";
        busy = false;
    }

    async void Save()
    {
        busy = true;
        status = editingId > 0 ? "Updating..." : "Saving...";
        string error = await MindscapeCloud.SavePlayerNote(editingId, title, body);
        status = error ?? "Saved.";
        if (error == null) ClearEditor();
        busy = false;
    }

    async void Delete(long id)
    {
        busy = true;
        status = "Deleting...";
        string error = await MindscapeCloud.DeletePlayerNote(id);
        status = error ?? "Deleted.";
        if (error == null && editingId == id) ClearEditor();
        busy = false;
    }

    void ClearEditor()
    {
        editingId = 0;
        title = "";
        body = "";
    }
}
```

## 5. Test it in the game

1. Wait for Unity to compile. Fix every red Console error before continuing.
2. Open a scene that can be entered after signing in, or temporarily use `main_menu_new.unity`.
3. Create an empty GameObject named `Player Notes Demo`.
4. Add the `PlayerNotesDemo` component.
5. Save the scene and enter Play Mode.
6. Sign in, then click **Reload notes**.
7. Create two notes, edit one and delete the other.
8. Stop and restart Play Mode. Reload; the remaining note must return from Supabase.
9. Sign in as a different test account. It must see an empty/different list and must not be able to edit the first account's notes.
10. In Supabase **Table Editor ▸ player_notes**, confirm different accounts have different `player_id` values.

The raw `player_id` is intentionally not returned to Unity. The game needs the note content, not another account identifier.

## 6. Use the data in production UI

The demo's `OnGUI` is intentionally disposable. In a real UI Toolkit screen:

1. Call `await MindscapeCloud.LoadPlayerNotes()` when the page opens.
2. Build one row per item in `MindscapeCloud.PlayerNotes`.
3. Call `SavePlayerNote(0, title, body)` to create.
4. Call `SavePlayerNote(existing.id, title, body)` to edit.
5. Ask for confirmation before `DeletePlayerNote(existing.id)`.
6. Disable buttons while a request is running and show the returned error string.
7. Subscribe to `MindscapeCloud.Changed` if the screen must refresh after another system changes cloud state; unsubscribe in `OnDisable`.

Never put the publishable key, access token or RPC URL in the UI script. All transport stays in `MindscapeCloud`.

<a id="supabase-notes-offline"></a>

## 7. Add offline support when required

The code above returns “Sign in” while offline. For a feature that must work offline, follow the existing `MindscapeDatabase` pattern:

1. Increment `SchemaVersion` in `MindscapeDatabase.cs`.
2. Add a local `player_notes` table in `CreateSchema()` with an integer ID, title, body and timestamps.
3. Add local save/list/delete methods using the existing parameterized `Write`, `Read` and SQLite query helpers.
4. Mirror the latest list into a profile-scoped PlayerPrefs key for WebGL, where SQLite may be unavailable.
5. Route through a single public facade: signed in → `MindscapeCloud`; offline → local database/PlayerPrefs.
6. Decide explicitly whether offline notes are uploaded after sign-in. Mindscape currently keeps offline and account data separate, so the least surprising default is **do not merge automatically**.

Do not silently drop offline writes or pretend a cloud save succeeded. The UI should state whether data is “Saved to your account” or “Saved on this device.”

## Adapt this example for another table

When creating inventory, achievements, custom profiles or another per-player feature, change all of these together:

| Layer | Change |
| --- | --- |
| Table | Columns, checks, foreign keys, index and cascade behavior |
| RPC input | Accept only values the player is allowed to choose; never accept `player_id` |
| RPC ownership | Resolve the caller and include that player ID in every read/update/delete filter |
| Permissions | Enable RLS, revoke direct table grants, restrict function execution |
| Unity DTO | Match PostgreSQL result column names exactly because `JsonUtility` maps field names |
| Unity validation | Match server length/range rules for quick feedback; keep server validation authoritative |
| Session clearing | Clear every account-specific in-memory cache in `ClearSession()` |
| Offline behavior | Implement local storage or clearly require sign-in |
| Testing | Two accounts, signed-out caller, invalid input, update/delete ownership, restart and target build |

Avoid using `select *` in RPC return queries after release; list fields explicitly so a future private database column is not accidentally sent to the game.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| Unity gets RPC `404` | Migration was applied to the same project used by `MindscapeCloud.RpcUrl`; function names match exactly |
| `permission denied for function` | Execute was granted to `authenticated`, and the player is actually signed in |
| `permission denied for table` | Unity called the table directly, or the function is not `security definer`; use the documented RPC path |
| Every player sees the same rows | A read query forgot `where player_id = private.player_from_token(...)` |
| One player can edit another row | Update/delete filters accept or trust a client player ID; resolve ownership on the server instead |
| Save succeeds but Unity list is empty | DTO field names do not match returned column names, or `JsonUtility` did not receive the top-level array through `Wrap(...)` |
| Notes survive logout in the UI | `playerNotes.Clear()` is missing from `ClearSession()` |
| `401` after a long session | Use the existing `Call(...)` helper rather than a separate `UnityWebRequest`; it refreshes and retries |
| Works in Editor but not WebGL | Check browser network/CORS errors and use the existing HTTPS project URLs; do not use a local database URL in the build |

Official references: [Supabase database functions](https://supabase.com/docs/guides/database/functions), [Row Level Security](https://supabase.com/docs/guides/database/postgres/row-level-security), and [securing the Data API](https://supabase.com/docs/guides/api/securing-your-api).
