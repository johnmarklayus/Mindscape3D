---
id: create-npc-model
group: Art
nav: Create an NPC model
---

# Create an NPC Model and Use It in Unity

The standalone NPC Maker starts from the game's boy or girl character model. Use it to make a visual variant, then set up the exported model as a gameplay NPC in Unity.

## 1. Create and export the model

1. In a terminal at the repository root, run:

   ```bash
   cd tools/npc-maker
   npm install
   npm run dev
   ```

   Open the local URL printed by Vite.
2. Enter a character name. Use the arrows to choose **Boy** or **Girl**, then choose hair and other available parts. Adjust the material colors.
3. Preview **T-pose**, **Idle**, **Walk**, **Run**, and **Talk**. Check that the full body and any added parts move together.
4. Click **Export model** to download the `.glb`. Keep a copy outside the Unity `Assets/` folder as your source export. **Save recipe** optionally downloads a `.npc.json` file with the editor settings; this JSON is not a Unity model.

The preview uses animations from the game, but **Export model does not include those animation clips**. The GLB contains the character mesh, materials, skeleton, and selected parts. Set up its Animator in Unity.

## 2. Import the GLB into Unity

1. Open the Unity project. In Unity's **Project** window, create a folder under `Assets/Characters/NPCs/` for custom models, then drag the exported `.glb` into it. This project includes **glTFast** for GLB import.
2. Drag the imported model into a temporary scene. Inspect the materials, hair and other parts, skeleton, size, facing direction, and whether its feet touch the floor. Fix the model or adjust its placement before using it in a scene.
3. Make a **model prefab** under `Assets/Prefabs/NPCs/Models/` from that imported model. Add an **Animator** to the model prefab and assign a compatible controller and game animation clips. The existing NPC prefab builder uses `Assets/BaldCharacter.controller`, but confirm that its clips animate this exported skeleton correctly in Unity. The browser preview alone does not establish Unity animation compatibility.

## 3. Make it an interactive NPC

1. In Unity, choose **GameObject → NPC**. The project creates an NPC object with a `CapsuleCollider`, the `NPC` component, and its interaction manager if needed.
2. In the NPC Inspector, set **NPC Name** and **3D Model** to your new model prefab. Changing the model refreshes its **Model** child automatically; use **Refresh 3D Model** if you need to rebuild that preview. Adjust **Model Offset** if needed. The `NPC` script aligns the rendered feet to the NPC root when it refreshes the model.
3. Fit the CapsuleCollider around the character. Set an interaction radius, dialogue nodes and choices, and, if needed, a face focus transform for the conversation camera.
4. Save the NPC object as a new prefab under `Assets/Prefabs/NPCs/`, then place it in the intended scene. Enter **Play** mode and check appearance, floor contact, Idle/Walk/Run animation, collider, facing, and dialogue interaction.

**The “Mindscape → NPCs → Build All 20 NPC Prefabs” menu is for the fixed 20-character roster.** It will not automatically register a new NPC Maker export. Use the manual prefab steps above for a new character.
