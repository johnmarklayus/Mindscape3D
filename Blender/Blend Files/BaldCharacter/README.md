# Bald character

Stylized bald character based on the supplied reference. Teal shirt, charcoal shorts, simple matte black ankle boots. Faces -Y in Blender; Z is up.

- BaldCharacter.blend: editable character, 17-bone skeleton, studio cameras and six actions. Saved in T-pose.
- BaldCharacter.glb: skinned character and all six animation clips, without the studio.
- preview.png: rendered T-pose preview.

Select BaldCharacter_Rig, open the Dope Sheet in Action Editor mode, and choose an action. Playback uses 24 fps.

| Action | Duration | Behavior |
|---|---:|---|
| Idle | 3 s | Looping breathing and head movement |
| Walk | 1 s | In-place loop |
| Run | 0.75 s | In-place loop |
| Conversation | 4 s | Looping hand gestures and nodding |
| Sit_Down | 1.5 s | Transition into sitting |
| Seated_Idle | 3 s | Seated breathing loop |

These are procedural body animations; conversation has no audio lip sync. Sitting assumes a seat around 0.54 Blender units high; no chair is included. The rest pose has horizontal arms and no hair.
