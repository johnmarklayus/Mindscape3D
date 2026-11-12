---
id: system-audio
group: Core Systems
nav: Music & SFX
---

# Music & SFX

Both are self-bootstrapping persistent singletons: you never place them in a scene.

## MusicManager

`MusicManager` spins up via `[RuntimeInitializeOnLoadMethod(BeforeSceneLoad)]` and plays the background music for the whole game.

- **Tracks** are every clip in `Resources/Music` (the Mindscape theme, `bgm`, is one of them). Clips import as *Streaming*.
- **Per scene:** `Resources/SceneMusicMap` maps a scene-name prefix to a track (the longest matching prefix wins) and sets the crossfade length. A scene with no entry keeps whatever is playing. Tracks listed under *Reserved Tracks* stay out of the Next playlist and only play where an entry names them.
- **Crossfades:** two AudioSources trade places so one track fades out while the next fades in. Call `MusicManager.PlayTrack("name")` to switch mid-story (the Chapter 3 Episode 8 walk does this).
- **Fades:** `FadeOut` / `FadeTo` and `LoadSceneFaded` (fade, then load) keep menu exits free of hard cuts. `SetDucked(true)` lowers the music to about 40% while settings are open so the sliders can be heard.
- **Options > Audio:** *Next* skips to the next playlist track, *Stop* / *Play* turns the music off or on, and both are remembered (`Mindscape.MusicStopped`). The "now playing" line listens to `MusicManager.Changed`. Volume is the `Mindscape.Music` PlayerPrefs value.
- **One music source only:** a scene must not carry its own looping music AudioSource. On every scene load MusicManager silences any other long looping source (short loops such as alarms and engines are kept). In Unity 6 an AudioSource plays its `Resource`, not the old clip field, so check that when searching scenes for audio.
- The Intro scene holds the music (`SetPaused`) while its story video plays, then resumes it for the title card.
- The playlist is royalty-free music (Kevin MacLeod, CC BY 4.0, credited in Options > Audio and `Music/CREDITS.txt`). Copyrighted game tracks are not included; drop tracks you own into `Resources/Music`.

## SFXManager

`SFXManager` does the same for one-shot sounds (`Mindscape.SFX` volume) and even synthesises its own UI click sound in code, so no imported audio asset is needed for that one. Call `SFXManager.Play(clip)` or `SFXManager.PlayClick()` from anywhere.
