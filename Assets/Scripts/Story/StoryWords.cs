using System;
using System.Collections.Generic;
using UnityEngine;

namespace Mindscape.AcademicPressure
{
    /// <summary>
    /// Every line the story scripts of Chapters 1–3 show (dialogue, thoughts, choices, cards, objectives, prompts),
    /// editable in the Inspector without opening a script. The scripts wrap their words in W("..."); when the same words
    /// have a Changed text here, that text is shown instead. Empty Changed: the script's own words.
    /// One asset: Assets/Resources/Story/Dialogue Words.asset (Mindscape › Story › Edit Dialogue Words).
    /// </summary>
    [CreateAssetMenu(menuName = "Mindscape/Dialogue Words", fileName = "Dialogue Words")]
    public class StoryWords : ScriptableObject
    {
        [Serializable]
        public class Entry
        {
            [Tooltip("The words as written in the script. Do not edit: this is how the line is found.")]
            public string original = "";
            [Tooltip("What the player sees instead. Empty: the original words.")]
            [TextArea(1, 6)] public string changed = "";
            [Tooltip("Where the line is: the script and its line number.")]
            public string where = "";
            [Tooltip("The episode or part of the story it belongs to.")]
            public string group = "";
            [NonSerialized] public bool missing;
        }

        public const string ResourcePath = "Story/Dialogue Words";
        public List<Entry> entries = new List<Entry>();

        static Dictionary<string, string> changes;

        /// <summary>The words to show for a line written in a script: the Inspector's change, or the line itself.</summary>
        public static string W(string original)
        {
            if (original == null) return null;
            if (changes == null) Load();
            return changes.TryGetValue(original, out var changed) ? changed : original;
        }

        static void Load()
        {
            changes = new Dictionary<string, string>();
            var asset = Resources.Load<StoryWords>(ResourcePath);
            if (asset == null) return;
            foreach (var e in asset.entries)
                if (!string.IsNullOrEmpty(e.original) && !string.IsNullOrEmpty(e.changed) && e.changed != e.original)
                    changes[e.original] = e.changed;
        }

        void OnValidate() => changes = null;   // an edit in the Inspector shows the next time the line plays

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.SubsystemRegistration)]
        static void ResetOnPlay() => changes = null;
    }
}
