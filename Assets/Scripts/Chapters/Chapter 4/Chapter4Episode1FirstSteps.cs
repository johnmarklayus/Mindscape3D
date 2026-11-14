using System.Collections;
using Mindscape.AcademicPressure;
using Mindscape.Data;
using UnityEngine;

namespace Mindscape.Story
{
    // Chapter 4 · Episode 1 · First Steps
    // Made with Mindscape › Story › New Episode. The places live in the scene (drag them in the Scene view); the order
    // of events and the words live here. See the Onboarding page, "Make an episode".
    public sealed class Chapter4Episode1FirstSteps : AcademicEpisode
    {
        [Header("Scene points (drag them in the Scene view)")]
        public Transform spawn;
        public Transform openingView;
        [Tooltip("Places the player walks to, in order. Each gets an [E] prompt and the lines below.")]
        public Transform[] spots = new Transform[0];

        public override int Chapter => 4;
        public override int Episode => 1;
        protected override float TimeLimit => 600;   // seconds of free roaming; dialogue and minigames pause it
        protected override string CompletionKey => MindscapeDatabase.ProfileKey("Mindscape.Story.Chapter4Episode1FirstSteps");
        protected override string NextScene => "";   // the next episode's scene name, or "" for the main menu
        protected override string ContinueLabel => "Main menu";
        protected override string CompletionNext => "EPISODE COMPLETE";

        protected override IEnumerator Play()
        {
            if (spawn != null) Teleport(spawn.position, spawn.eulerAngles.y);
            if (openingView != null) Shot(openingView.position, openingView.position + openingView.forward * 8);
            yield return Card("CHAPTER 4\n<size=60%>Episode 01 · First Steps</size>");
            yield return Say("Narration", "Write the opening line here.");

            // One stop per spot: walk there, press E, read the lines.
            for (int i = 0; i < spots.Length; i++)
            {
                bool done = false;
                AddSpot(spots[i], "Look", () => !done, () => Stop(() => done = true));
                SetObjective("First Steps", Check(false, "Find the marked place"));
                yield return RoamUntil(() => done);
            }

            Complete("First Steps", "Write the closing words here.");
        }

        IEnumerator Stop(System.Action done)
        {
            yield return Think("Something Joey thinks here.");
            yield return Me("Something Joey says here.");
            done();
        }
    }
}
