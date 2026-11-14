using System;
using System.Collections.Generic;
using UnityEngine;

namespace Mindscape.Cutscenes
{
    /// <summary>
    /// A slide cutscene made in the editor: pictures with words, one after another (Mindscape › Story › New Cutscene…).
    /// It plays before an episode (the chapter asset's "Cutscene Before"), from a Cinematic step, or as a scene of its
    /// own (CutsceneScene). Everything is edited in the Inspector.
    /// </summary>
    [CreateAssetMenu(menuName = "Mindscape/Cutscene", fileName = "Cutscene")]
    public class CutsceneAsset : ScriptableObject
    {
        [Tooltip("The slides, in order. Drag to reorder.")]
        public List<CutsceneSlide> slides = new List<CutsceneSlide>();

        [Header("Look and sound")]
        [Tooltip("Seconds each slide takes to fade in and out.")]
        [Min(0)] public float fadeSeconds = .6f;
        [Tooltip("Music while the cutscene plays (the game's music pauses). Empty: the game's music keeps playing.")]
        public AudioClip music;
        [Range(0, 1)] public float musicVolume = .6f;
        [Tooltip("Let the player skip the rest with Esc (or the gamepad's Start button).")]
        public bool canSkip = true;

        [Header("Only for a cutscene scene of its own")]
        [Tooltip("The scene to open when the cutscene ends (for example \"Chapter 4 - Episode 1\"). Empty: the main menu.")]
        public string nextScene = "";
    }

    [Serializable]
    public class CutsceneSlide
    {
        [Tooltip("The picture, shown full screen (it fills the screen and is cropped at the edges if needed).")]
        public Texture2D image;
        [Tooltip("Who speaks (shown above the words). Empty for narration.")]
        public string speaker = "";
        [Tooltip("The words under the picture. \"Joey\" is replaced by the player's name.")]
        [TextArea(2, 6)] public string text = "";
        [Tooltip("Seconds before it moves on by itself. 0: wait for the player (Space, click, tap).")]
        [Min(0)] public float autoAdvanceSeconds = 0;
    }
}
