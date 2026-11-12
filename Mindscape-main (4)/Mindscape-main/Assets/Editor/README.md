# Editor tools

Scripts that run only inside the Unity Editor: the **Mindscape** menu, custom Inspectors, and the tools that build or update scenes. They are never part of a game build. Runtime scripts are in `Assets/Scripts/`.

| Folder | What is in it |
|---|---|
| `Chapters/` | Scene builders for each chapter (`AcademicPressureBuilder*` for Chapter 1, `FamilyExpectationsBuilder` for Chapter 2, `SocialDynamicsBuilder` for Chapter 3), keepsakes and flashbacks. `Chapters/Prototypes/` holds the old, superseded Chapter 2 builders. |
| `World/` | The shared city and house models (WorldModelSync, HouseModelSync, HouseSpareRooms, BedroomLayout), the school, doors, furniture, traffic, street life, LOD setup |
| `Characters/` | Player boy and girl models, NPC prefabs and model import fixes, family animators |
| `UI/` | Builders for the HUD, pause menu, mobile controls, main menu scene, and the episode thumbnails |
| `Menus/` | GameObject menu items and Inspectors for collectibles, NPCs, quests and minigames |
| `Tests/` | Checks you can run from the menu or in batch mode (episode verifications, story shot clearance, ShotProbe) |
| `Build/` | Command-line builds (used by `Tools/BuildScripts/*.sh`) and import settings |

Every one of these folders sits under a folder named `Editor`, which is what keeps it out of the build. Keep new tools inside `Assets/Editor/`.
