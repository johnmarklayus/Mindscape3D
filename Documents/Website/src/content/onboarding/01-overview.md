---
id: overview
group: Getting Started
nav: What you are building
---

# What You Are Building

Start here. This onboarding follows Mindscape 3D through its whole life, from an empty computer to a published release. Pick a topic in the sidebar, or use **Next** at the bottom of each page to read it in order.

Mindscape 3D is a third-person story game made in **Unity 6** about the everyday pressures students face. The player plays as **Joey**, as a boy or a girl. Joey explores the house, the school and the city, talks with family and friends, makes choices, and practises coping skills: guided breathing, grounding, and putting a worried thought "on trial" in the Worry Courtroom. After each episode, the player writes in a reflection journal and fills in a short self-assessment.

| Chapter | Episodes | Setting |
|---|---|---|
| Tutorial | 1 | Movement, the menu and the journal |
| 1 · Academic Pressure | 4 | House, classroom, cafeteria, dormitory: one school deadline |
| 2 · Family Expectations | 5 | An examination day and the family at home |
| 3 · Social Dynamics | 8 | A reunion with old friends, the walk home, the mirror |

The game ships on **WebGL (browser), Android, macOS and Windows**. Progress is saved on the device (SQLite, or local storage in the browser). With an optional online account (Supabase), progress and the journal are also kept in the cloud.

## The pipeline at a glance

```text
 Blender (.blend)  ──export FBX/GLB──▶  Unity Assets/Models, Assets/Characters
                                              │
 Story spec (PDF) ──▶ episode script (C#) ──▶ │  scenes edited in Unity (Scene view, Inspector)
                                              ▼
                                    Assets/Scenes/*.unity  (one scene per episode)
                                              │
                    Play-test in the editor + tester lists + QA workbook
                                              │
                     Tools/BuildScripts/*.sh  (Unity in batch mode)
                                              ▼
                    Builds/<date>/  APK · macOS app · Windows exe · WebGL
                                              │
           ┌──────────────────────────────────┼──────────────────────────────┐
           ▼                                  ▼                              ▼
  Builds/webgl-play → Vercel         Site/ (official website)       Documents/Website
  (play in the browser)              downloads + /play page          (this documentation)

 supabase/ (database migrations + "account" edge function) ◀── the game talks to it over HTTPS
```
