# MindScape NPC Maker

Standalone character editor using the game's actual home character assets: `Assets/Characters/Player/Boy_Home.glb` and `Assets/Characters/Player/Girl_Home.fbx`. The girl FBX is converted to GLB for browser display using `scripts/export-game-models.py`.

Run `npm install`, then `npm run dev` from this directory. Open the local URL printed by Vite. `npm run build` produces a distributable app in `dist/`.

Choose a base, select the original hair or a style from `Blender/Npc-maker/Hair`, a hat (`Hats`), eyes / nose / mouth (`Face`) and a shirt design (`Shirts`), recolor materials, preview the game's actual Idle/Walk/Run/Conversation clips, and export a GLB or JSON recipe. The animation GLBs are generated from `Joey_Actions.fbx` and `NPC_17_Penelope.fbx` using `scripts/export-game-animations.py`; their clips are retargeted to the home models in the viewer. The hair meshes are bound to the game skeleton so they move with the clips and remain attached in the exported GLB. Animation controller setup happens in Unity.

## Hats, face parts and shirt designs

All of these are built in `Blender/Npc-maker/NPC_Maker_Base_And_Hair.blend` and bound to the game rig by bone name, like the hair. One file fits the boy and the girl (their rigs and heads are the same).

- **Face** (`public/models/face`): choosing eyes hides the model's eye meshes; a nose or mouth hides the default nose (the small pyramid in the skin) or the smile (the brows stay) by leaving those triangles out of the index. A nose uses the character's skin material.
- **Hats** (`public/models/hats`): Chef's hat, Baseball cap, Beret. Large hairstyles (Curly, Long) can show through a hat.
- **Shirts** (`public/models/shirts`): a UV-mapped copy of the shirt with a black/white design mask. The app paints the mask with the Shirt colour and the Design colour into a texture, so an exported GLB keeps the design.
