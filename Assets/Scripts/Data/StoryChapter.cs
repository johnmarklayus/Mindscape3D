using System;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;

namespace Mindscape.Data
{
    /// <summary>
    /// A chapter made in the Unity editor (Chapter 4 and later): its name, picture and episodes. Made with
    /// Mindscape › Story › New Chapter… and kept in Assets/Resources/Chapters/. The main menu (chapter card and episode
    /// list), the loading screen, progress and unlocking, and the journal read it, so a new chapter needs no code.
    /// Chapters 1–3 keep their own data in code.
    /// </summary>
    [CreateAssetMenu(menuName = "Mindscape/Story Chapter", fileName = "Chapter")]
    public class StoryChapter : ScriptableObject
    {
        [Tooltip("The chapter's number: 4 for the first new chapter, then 5, 6… Chapters follow each other without gaps.")]
        [Min(StoryChapters.FirstNumber)] public int number = StoryChapters.FirstNumber;
        [Tooltip("The chapter's name, for example \"New Beginnings\".")]
        public string title = "New Chapter";
        [Tooltip("One or two sentences about the chapter (shown under the chapter's episode list).")]
        [TextArea(2, 4)] public string description = "";
        [Tooltip("The chapter's picture: its card in the main menu, and the loading screen of any episode without a picture of its own.")]
        public Texture2D thumbnail;
        [Tooltip("The journal question after each episode. Leave empty for the usual one.")]
        [TextArea(1, 3)] public string journalPrompt = "";
        [Tooltip("The episodes, in order. Mindscape › Story › New Episode… adds one here when it makes the scene.")]
        public List<StoryEpisodeInfo> episodes = new List<StoryEpisodeInfo>();

        public string Badge => "CHAPTER " + number.ToString("00") + "  ·  " + (title ?? "").ToUpperInvariant();

#if UNITY_EDITOR
        void OnValidate() => StoryChapters.Reload();
#endif
    }

    [Serializable]
    public class StoryEpisodeInfo
    {
        [Tooltip("The episode's name, for example \"First Steps\".")]
        public string title = "New Episode";
        [Tooltip("The scene's name, as in File › Build Profiles, for example \"Chapter 4 - Episode 1\".")]
        public string scene = "";
        [Tooltip("Where it happens, shown on the loading screen, for example \"JOEY'S HOUSE\".")]
        public string location = "";
        [Tooltip("What the player will do, shown on the loading screen (one to three short lines).")]
        [TextArea(2, 4)] public string briefing = "";
        [Tooltip("The loading screen and menu picture of this episode. Empty: the chapter's picture.")]
        public Texture2D thumbnail;
        [Tooltip("A slide cutscene that plays when the episode starts, before anything else (Mindscape › Story › New Cutscene…).")]
        public Mindscape.Cutscenes.CutsceneAsset cutsceneBefore;

        public Texture2D Picture(StoryChapter chapter) => thumbnail != null ? thumbnail : chapter != null ? chapter.thumbnail : null;
    }

    /// <summary>The chapters made in the editor, as the game sees them.</summary>
    public static class StoryChapters
    {
        public const int FirstNumber = 4;
        public const string ResourcesFolder = "Chapters";
        static StoryChapter[] all;

        /// <summary>Every chapter asset (Chapter 4 and later), by number.</summary>
        public static StoryChapter[] All => all ??= Resources.LoadAll<StoryChapter>(ResourcesFolder)
            .Where(c => c != null && c.number >= FirstNumber).OrderBy(c => c.number).ToArray();

        public static void Reload() => all = null;

        /// <summary>
        /// The chapters players can reach: 4, 5, 6… without a gap, each with at least one episode. A chapter after a gap
        /// (a 6 with no 5) or without episodes is left out until it is complete.
        /// </summary>
        public static IEnumerable<StoryChapter> Playable
        {
            get
            {
                int expect = FirstNumber;
                foreach (var c in All)
                {
                    if (c.number != expect || c.episodes.Count == 0) yield break;
                    yield return c;
                    expect++;
                }
            }
        }

        public static StoryChapter Get(int number) => Playable.FirstOrDefault(c => c.number == number);

        public static StoryEpisodeInfo Episode(int chapter, int episode)
        {
            var c = Get(chapter);
            return c != null && episode >= 1 && episode <= c.episodes.Count ? c.episodes[episode - 1] : null;
        }

        /// <summary>Which chapter and episode a scene belongs to.</summary>
        public static bool Find(string scene, out int chapter, out int episode)
        {
            chapter = episode = 0;
            if (string.IsNullOrEmpty(scene)) return false;
            foreach (var c in Playable)
                for (int i = 0; i < c.episodes.Count; i++)
                    if (c.episodes[i].scene == scene) { chapter = c.number; episode = i + 1; return true; }
            return false;
        }

        /// <summary>The scene of the chapter's first episode, or "".</summary>
        public static string FirstScene(int chapter) => Episode(chapter, 1)?.scene ?? "";

        /// <summary>The scene after this episode: the chapter's next episode, else the next chapter's first, else "".</summary>
        public static string NextScene(int chapter, int episode)
        {
            var next = Episode(chapter, episode + 1);
            return next != null ? next.scene : FirstScene(chapter + 1);
        }
    }
}
