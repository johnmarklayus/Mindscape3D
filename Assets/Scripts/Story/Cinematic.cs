using System;
using System.Collections.Generic;
using Mindscape.Cutscenes;
using Mindscape.Minigames;
using UnityEngine;

namespace Mindscape.AcademicPressure
{
    /// <summary>
    /// A cinematic moment made in the Inspector: a list of steps (camera cuts and glides, lines of dialogue, pictures,
    /// fades, people walking and turning, objects appearing…) that the episode plays in order. When it plays is set by
    /// Trigger: at the start of the episode, when the player walks to a place, or when the player presses [E] at a place.
    /// Made with Mindscape › Story › New Cinematic. Works in every episode scene.
    /// </summary>
    [AddComponentMenu("Mindscape/Cinematic")]
    public class Cinematic : MonoBehaviour
    {
        public enum When
        {
            [InspectorName("At the start of the episode")] AtStart,
            [InspectorName("When the player walks to a place")] OnArrival,
            [InspectorName("When the player presses E at a place")] OnInteract,
            [InspectorName("Only when a script plays it")] FromScript,
        }

        [Tooltip("When this cinematic plays.")]
        public When trigger = When.OnInteract;
        [Tooltip("The place the player walks to (or presses E at). A child object of this one, moved where it should be.")]
        public Transform place;
        [Tooltip("The words of the [E] prompt, for example \"Talk to Mom\".")]
        public string prompt = "Look";
        [Tooltip("How close the player must be, in metres.")]
        [Min(.5f)] public float range = 2.5f;
        [Tooltip("Play it only the first time.")]
        public bool onlyOnce = true;

        [Tooltip("What happens, in order. Click + to add a step, then pick its Type.")]
        public List<CinematicStep> steps = new List<CinematicStep>();

        [NonSerialized] public bool played;

#if UNITY_EDITOR
        void OnDrawGizmos()
        {
            if (place != null && trigger != When.AtStart && trigger != When.FromScript)
            {
                Gizmos.color = new Color(1f, .85f, .3f);
                Gizmos.DrawWireSphere(place.position, .35f);
                UnityEditor.Handles.color = Gizmos.color;
                UnityEditor.Handles.DrawWireDisc(place.position, Vector3.up, range);
                UnityEditor.Handles.Label(place.position + Vector3.up * 1.2f, name + (trigger == When.OnInteract ? "  [E] " + prompt : "  (on arrival)"));
            }
        }

        void OnDrawGizmosSelected()
        {
            for (int i = 0; i < steps.Count; i++)
            {
                var s = steps[i];
                if ((s.type == CinematicStep.Type.CameraCut || s.type == CinematicStep.Type.CameraGlide) && s.target != null)
                {
                    Gizmos.color = new Color(.35f, .7f, 1f);
                    Gizmos.matrix = Matrix4x4.TRS(s.target.position, s.target.rotation, Vector3.one);
                    Gizmos.DrawFrustum(Vector3.zero, 50, 1.2f, .1f, 16f / 9f);
                    Gizmos.matrix = Matrix4x4.identity;
                    UnityEditor.Handles.Label(s.target.position + Vector3.up * .3f, "Step " + (i + 1) + ": " + s.target.name);
                }
            }
        }
#endif
    }

    [Serializable]
    public class CinematicStep
    {
        public enum Type
        {
            [InspectorName("Camera: cut to a view")] CameraCut,
            [InspectorName("Camera: glide to a view")] CameraGlide,
            [InspectorName("Dialogue: a line")] Line,
            [InspectorName("Dialogue: a choice")] Choice,
            [InspectorName("Screen: title card")] TitleCard,
            [InspectorName("Screen: fade to black")] FadeOut,
            [InspectorName("Screen: fade from black")] FadeIn,
            [InspectorName("Screen: show a picture")] ShowPicture,
            [InspectorName("Screen: hide the picture")] HidePicture,
            [InspectorName("Screen: play a cutscene")] PlayCutscene,
            [InspectorName("Person: walk to a place")] PersonWalk,
            [InspectorName("Person: stand at a place")] PersonPlace,
            [InspectorName("Person: turn to look at")] PersonTurn,
            [InspectorName("Person: play an animation")] PersonAnimation,
            [InspectorName("Player: move to a place")] PlayerMove,
            [InspectorName("Object: show")] ShowObject,
            [InspectorName("Object: hide")] HideObject,
            [InspectorName("Breathing exercise")] Breathing,
            [InspectorName("Wait")] Wait,
            // Added later: new types go at the end so the steps already made keep their type.
            [InspectorName("Dialogue: a conversation (asset)")] Conversation,
            [InspectorName("Dialogue: write an answer")] WriteAnswer,
            [InspectorName("Phone: open a chat")] PhoneOpen,
            [InspectorName("Phone: a message")] PhoneMessage,
            [InspectorName("Phone: pick a reply")] PhoneReply,
            [InspectorName("Phone: close")] PhoneClose,
            [InspectorName("Screen: start a flashback")] FlashbackStart,
            [InspectorName("Screen: end the flashback")] FlashbackEnd,
            [InspectorName("Minigame: exam paper")] Exam,
            [InspectorName("Minigame: Worry Courtroom")] WorryCourtroom,
            [InspectorName("Minigame: practice game")] Practice,
            [InspectorName("Stress: raise or lower")] Stress,
        }

        public Type type = Type.Line;
        [Tooltip("Camera steps: the view (its position and the way it looks). Person and player steps: the place to go to, or to look at.")]
        public Transform target;
        [Tooltip("The person (Mom, Dad, Tim, a friend…): drag them from the Hierarchy.")]
        public Transform person;
        [Tooltip("Who speaks: a name (Mom, Justin…), \"Joey\" for the player, \"Thought\" for the player's thoughts, or empty for narration.")]
        public string speaker = "";
        [Tooltip("The words. \"Joey\" is replaced by the player's name.")]
        [TextArea(2, 6)] public string text = "";
        [Tooltip("The answers the player picks from.")]
        public List<string> options = new List<string>();
        [Tooltip("The name the answer is saved under, for example \"ch4_reply\". Never reuse a name for something else.")]
        public string saveAs = "";
        [Tooltip("Seconds it takes.")]
        [Min(0)] public float seconds = 1;
        public Texture2D picture;
        public CutsceneAsset cutscene;
        [Tooltip("The animation to play: Idle, Walk, Talk (people with the family's talk animations), or any state name of their Animator.")]
        public string animation = "Talk";
        public GameObject obj;
        [Tooltip("A conversation asset (Mindscape › Story › New Conversation).")]
        public Conversation conversation;
        [Tooltip("The examination paper (Assets › Create › Mindscape › Exam Paper).")]
        public Minigames.ExamPaper exam;
        [Tooltip("The worry on trial (Assets/Minigames/WorryCourtroom/Cases).")]
        public Minigames.WorryCourtroomCase worryCase;
        [Tooltip("The minigame prefab (Assets/Prefabs/Minigames).")]
        public GameObject minigame;
        [Tooltip("How much stress: a positive number raises it, a negative number lowers it (the meter goes from 0 to 100).")]
        public float amount = 10;
    }
}
