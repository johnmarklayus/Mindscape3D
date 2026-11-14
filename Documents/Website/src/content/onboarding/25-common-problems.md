---
id: common-problems
group: Help
nav: Common problems
---

# Common Problems

Symptoms seen during development, what causes them and the fix.

| Symptom | Cause and fix |
|---|---|
| Build stops at once: "another Unity instance" | The editor still has the project open. Close it, or delete a stale `Temp/UnityLockfile`. |
| Build fails with "scripts are compiling" | It started straight after a platform switch. Wait for compiling to finish, then build again. |
| Web build shows a decompression error | The host isn't sending `Content-Encoding: br`. Use the `vercel.json` in `Builds/webgl-play`. |
| Vercel: "File size limit exceeded (100 MB)" | An APK or zip was included. Add it to `.vercelignore` and host it elsewhere. |
| NPCs 100× too big after an export | FBX scale setting. Re-export with *FBX Units Scale*, then run the NPC scale repair. |
| Objects float, or invisible walls near a model | Its colliders were sized on an older import. Refit them (for the bed: **Mindscape › House › Refit Joey Bed Colliders**). |
| "[E] Talk" appears with nobody there | An NPC was hidden while the talk system still had it listed. Hidden NPCs are now skipped; hide NPCs with `SetActive(false)`. |
| Broken references after moving files | The `.meta` was not moved with the file. Move files only inside Unity. |
| GitHub rejects a push | A file is over 100 MB (builds, the full-size intro video). Keep them in `.gitignore`. |
| A change made in a scene disappeared | A legacy chapter builder was run (**Mindscape › Legacy Builders**). It regenerates scenes from code; restore the scene from git and edit by hand instead. |

More: [Conventions & Gotchas](/#ref-conventions) · [Handover Guide](/#handover) · [Gabay sa Handover](/#handover-tl)
