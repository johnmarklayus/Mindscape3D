---
id: build
group: Build & Deploy
nav: Build the game
---

# Build the Game

Make the APK, the macOS app, the Windows exe and the WebGL build.

## Version numbers

Set them in **Project Settings › Player** before a release:

- **Version** (`bundleVersion`), for example `0.3.0`
- **Android Bundle Version Code**: raise it by 1 for every APK you hand out, or installs over an older APK fail

## Command-line builds (recommended)

**Close Unity first.** Only one Unity can have the project open at a time. Then, from the project folder (Terminal on a Mac, Git Bash on Windows):

```bash
./Tools/BuildScripts/build-android.sh   # ~2–10 min → Builds/<date>/Mindscape-<date>.apk
./Tools/BuildScripts/build-mac.sh       # ~8 min     → Builds/<date>/Mindscape-macOS-<date>.zip
./Tools/BuildScripts/build-windows.sh   # ~9 min     → Builds/<date>/Mindscape-Windows-<date>.zip
./Tools/BuildScripts/build-webgl.sh     # ~15–26 min → Builds/<date>/Mindscape-WebGL-<date>.zip
```

Each script starts Unity in batch mode with `CommandLineBuild.<Platform>` (`Assets/Editor/Build/CommandLineBuild.cs`), shows progress lines, and writes a log to `Builds/<date>/logs/`. A good build ends with `Build Finished, Result: Success`. To build all four in a row (about 35 minutes):

```bash
for p in android mac windows webgl; do ./Tools/BuildScripts/build-$p.sh || break; done
```

You can also build from the editor with **File › Build Profiles › Build**. If you switch platform first, wait until scripts have finished compiling, or the build fails with "scripts are compiling".

## Platform notes

| Platform | Notes |
|---|---|
| Android | Debug-signed unless you set up a release keystore (**Player › Publishing Settings**). Install with `adb install -r <apk>`. Set a real `applicationIdentifier` before publishing to a store. The custom manifest holds the `mindscape://` link used by Google sign-in. |
| macOS | ARM64, Mono, ad-hoc signed, not notarised. The first time, players right-click the app and choose **Open**. The sign-in plugin source is in `Tools/NativePlugins/`. |
| Windows | Mono. Players unzip and run `Mindscape.exe` with its files beside it. |
| WebGL | IL2CPP, Brotli compression. The web host must serve `.br` files with `Content-Encoding: br`. |

Leave the `*_BurstDebugInformation_DoNotShip` folders out of anything you share.
