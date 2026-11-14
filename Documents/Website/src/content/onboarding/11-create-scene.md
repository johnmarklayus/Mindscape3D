---
id: create-scene
group: Scenes
nav: Create a scene
---

# Create a Scene

A new scene is either a new **episode** (use the New Episode tool) or a plain scene such as a test area or a minigame room.

## A new episode scene

Use **Mindscape › Story › New Episode…**: it copies the episode scene that looks most like the new place (house, school, reunion hall…), with its city, lighting, player and camera. See [Create an episode](#create-episode).

## A scene that is not an episode

For a test area or a minigame room: **File › New Scene**, add a floor, a light and the **Player** prefab (`Assets/Prefabs/Player.prefab`), then follow [Create a Gameplay Scene](/#workflow-scene). The Minigame Lab has its own tool (**Mindscape › Minigame Lab › Create or Open Test Scene**).

## Add it to the game

Open **File › Build Profiles** and add the scene to the scene list (New Episode does this for you). The game starts at `Intro`.
