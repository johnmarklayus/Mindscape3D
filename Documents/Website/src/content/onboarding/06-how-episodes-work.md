---
id: how-episodes-work
group: Story
nav: How an episode works
---

# How an Episode Works

Every story scene contains one **episode component**: a C# class that derives from `AcademicEpisode`. Its `Play()` coroutine is the episode's script, read from top to bottom.

```csharp
yield return Card("CHAPTER 3 · SOCIAL DYNAMICS\nEpisode 04 · The Corner of the Room");
yield return Visit(4, "A little space", "Sit by the window", "Maybe I shouldn't have come.");
yield return Choose(prompt, question, options, i => Response = i);
Complete(title, "You took another step through the evening.");
```

The base class handles the rest:

| Tool | What it does |
|---|---|
| `AddSpot` / `AddArrival` | A place in the world with an [E] prompt, or a trigger that fires when you walk there |
| `RoamUntil` | Free movement until a condition is met |
| `Say`, `Me`, `Think`, `DialogueSequence` | The dialogue box with its "x / n" counter |
| `Choose` | A choice screen; the answer is saved |
| `Shot`, `ShotOver`, `Glide` | Story camera shots that keep clear of walls and of the player's body |
| `SitAt` / `StandUpAt`, `LieInBed` / `GetUp` | Seated and lying poses |
| Breathing, Worry Courtroom, journal | Minigames and reflection screens shared by every chapter |
| Save replay | Every spot the player uses is recorded, so loading a save replays those steps and resumes where the player left off |
