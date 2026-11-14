---
id: test
group: Testing
nav: Test the game
---

# Test the Game

How changes are checked before a release.

1. **In the editor:** play the episode scene directly, then the full flow from `Intro`. Check it with keyboard and mouse, with a gamepad, and in mobile mode.
2. **Tester lists:** feedback is collected in `Documents/Tester Lists/`. Each fix is checked against its list item.
3. **QA workbook:** `Tools/QA/` writes the master workbook to `Documents/Reports/`. The test cases are on [QA Test Cases](/#ref-qa).
4. **Batch probe (with the editor closed):** `Assets/Editor/Tests/ShotProbe.cs` opens a scene in batch mode to render shots, cast rays or run builders. Use it to check where things are placed without opening Unity:

   ```bash
   /Applications/Unity/Hub/Editor/6000.5.8f1/Unity.app/Contents/MacOS/Unity -batchmode \
     -projectPath "$PWD" -executeMethod ShotProbe.Run \
     -probeFile cmds.txt -probeOut out/ -logFile out/unity.log -quit
   ```

   Commands, one per line: `open <scene>`, `shot name px py pz lx ly lz [fov]`, `find <text>`, `comp <object>`, `ray px py pz dx dy dz` (the ray's length is the direction's length), `method Type.Method`, `place obj x y z yaw`, `save`.
5. **Before every build:** check the Console for errors, and check that the scene list in Build Profiles is complete.
