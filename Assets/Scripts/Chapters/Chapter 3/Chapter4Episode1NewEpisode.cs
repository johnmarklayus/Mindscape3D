using System.Collections;
using Mindscape.AcademicPressure;
using UnityEngine;

namespace Mindscape.Story
{
    // Chapter 3 · Episode 10 · THIS IS TEST
    // Made with Mindscape › Story › New Episode. The places live in the scene (drag them in the Scene view); the order
    // of events and the words live here. The chapter and episode numbers, the time limit, the next scene and the save
    // are set by StoryEpisode from the Inspector and the chapter asset. See the Onboarding page, "Create an episode".
    public sealed class Chapter4Episode1NewEpisode : StoryEpisode
    {
        [Header("Scene points (drag them in the Scene view)")]
        public Transform spawn;
        public Transform openingView;
        [Tooltip("Places the player walks to, in order. Each gets an [E] prompt and the lines below.")]
        public Transform[] spots = new Transform[0];

        protected override IEnumerator Play()
        {
            if (spawn != null) Teleport(spawn.position, spawn.eulerAngles.y);
            if (openingView != null) Shot(openingView.position, openingView.position + openingView.forward * 8);
            yield return Card("CHAPTER 3\n<size=60%>Episode 10 · THIS IS TEST</size>");
            yield return Say("Narration", "Write the opening line here.");

            // One stop per spot: walk there, press E, read the lines.
            for (int i = 0; i < spots.Length; i++)
            {
                bool done = false;
                AddSpot(spots[i], "Look", () => !done, () => Stop(() => done = true));
                SetObjective("THIS IS TEST", Check(false, "Find the marked place"));
                yield return RoamUntil(() => done);
            }

            // Free walking until every cinematic set to play at a place has played (Mindscape › Story › New Cinematic).
            yield return RoamUntilCinematicsDone();

            Complete("THIS IS TEST", "Write the closing words here.");
        }

        IEnumerator Stop(System.Action done)
        {
            yield return Think("Something Joey thinks here.");
            yield return Me("Something Joey says here.");
            done();
        }
    }
}
