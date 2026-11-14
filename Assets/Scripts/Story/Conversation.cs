using System;
using System.Collections.Generic;
using UnityEngine;

namespace Mindscape.AcademicPressure
{
    /// <summary>
    /// A conversation written in the Inspector: lines, each with who speaks and the words. Played by a cinematic step
    /// (Dialogue: a conversation) or a script (yield return Talk(conversation);). The lines share one x / n counter.
    /// Made with Mindscape › Story › New Conversation; kept in Assets/Story/Conversations.
    /// </summary>
    [CreateAssetMenu(menuName = "Mindscape/Conversation", fileName = "Conversation")]
    public class Conversation : ScriptableObject
    {
        [Serializable]
        public class Line
        {
            [Tooltip("Who speaks: a name (Mom, Justin…), \"Joey\" for the player, \"Thought\" for the player's thoughts, or empty for narration.")]
            public string speaker = "";
            [Tooltip("The words. \"Joey\" is replaced by the player's name. Press Enter for a new line.")]
            [TextArea(2, 6)] public string words = "";
        }

        [Tooltip("The lines, top to bottom.")]
        public List<Line> lines = new List<Line>();
    }
}
