---
id: system-lighting
group: Core Systems
nav: Lighting & Rendering
---

# Lighting & Rendering

Episode 1 is lit flat and evenly, with no cast shadows, so every corner of the house is readable.

| Setting | Value | Where |
| --- | --- | --- |
| Directional light shadows | **None** | `Directional Light` in the scene |
| Directional light intensity | 0.9 | same |
| Ambient mode | **Flat**, a bright neutral colour (about 0.86 grey) | Lighting settings, saved in the scene |
| Screen Space Ambient Occlusion | **Off** for the PC quality level | `Assets/Settings/PC_Renderer.asset` |
| Roof | Seven pieces named "Roof" under `House And Lot`, enabled | Episode 1 scene |

## Notes

- The **SSAO** feature darkens corners and contact points, which reads as shadow. It lives in the shared PC renderer asset, so turning it off affects every scene on the PC quality level, not just Episode 1. Re-tick **Screen Space Ambient Occlusion** on `PC_Renderer` to bring it back. The Mobile renderer has no such feature.
- To bring shadows back in a single scene, set the directional light's **Shadow Type** to *Soft Shadows* and lower the ambient intensity.
- The roof pieces were hidden at one point (inactive in the Hierarchy). Toggle them to show or hide the roof.
