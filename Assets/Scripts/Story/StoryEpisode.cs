using Mindscape.Data;
using UnityEngine;

namespace Mindscape.AcademicPressure
{
    /// <summary>
    /// The base of every episode made with Mindscape › Story › New Episode… (Chapter 4 and later). The chapter and
    /// episode numbers are set in the Inspector; the save key, the next scene, the Continue button and the completion
    /// line come from the chapter asset (StoryChapter), so the episode script only holds the story itself.
    /// </summary>
    public abstract class StoryEpisode : AcademicEpisode
    {
        [Header("Chapter and episode")]
        [Tooltip("The chapter this episode belongs to (4 or later). It must match the chapter asset in Assets/Resources/Chapters.")]
        [SerializeField] int chapterNumber = StoryChapters.FirstNumber;
        [Tooltip("The episode's number in its chapter: its place in the chapter asset's Episodes list (1 = first).")]
        [SerializeField] int episodeNumber = 1;
        [Tooltip("Seconds of free roaming before the episode's time runs out. Dialogue and minigames pause the timer.")]
        [SerializeField] float timeLimit = 600;

        public override int Chapter => chapterNumber;
        public override int Episode => episodeNumber;
        protected override float TimeLimit => timeLimit;
        protected override string CompletionKey => MindscapeProgress.CompletionKey(Chapter, Episode);
        protected override string NextScene => StoryChapters.NextScene(Chapter, Episode);
        bool NextIsNewChapter => StoryChapters.Episode(Chapter, Episode + 1) == null && StoryChapters.Get(Chapter + 1) != null;
        protected override string ContinueLabel => NextIsNewChapter ? "Begin Chapter " + (Chapter + 1) : "Continue";
        protected override string CompletionNext
        {
            get
            {
                var next = StoryChapters.Episode(Chapter, Episode + 1);
                if (next != null) return "NEXT: " + (next.title ?? "").ToUpperInvariant();
                var chapter = StoryChapters.Get(Chapter + 1);
                if (chapter != null) return "NEXT: " + chapter.Badge;
                return "CHAPTER " + Chapter + " COMPLETE";
            }
        }

        /// <summary>The episode's title from the chapter asset ("" when it is not listed there).</summary>
        protected string EpisodeTitle => StoryChapters.Episode(Chapter, Episode)?.title ?? "";
    }
}
