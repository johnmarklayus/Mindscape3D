using System;
using System.Collections.Generic;
using UnityEngine;

namespace Mindscape.Minigames
{
    /// <summary>
    /// An examination paper for the exam minigame (cinematic step "Minigame: exam paper", or a script's TakeExam):
    /// up to five questions with up to three answers each, a clock, and an optional 5-4-3-2-1 grounding break.
    /// No score is shown; the number answered can be saved. Create: Assets › Create › Mindscape › Exam Paper.
    /// </summary>
    [CreateAssetMenu(menuName = "Mindscape/Exam Paper", fileName = "Exam Paper")]
    public class ExamPaper : ScriptableObject
    {
        public const int MaxQuestions = 5, MaxAnswers = 3;

        [Serializable]
        public class Question
        {
            [TextArea(2, 6)] public string question = "";
            [Tooltip("Up to three answers.")]
            public List<string> answers = new List<string> { "", "", "" };
        }

        [Tooltip("How long the paper lasts, in seconds. When it runs out the bell rings; the player can still hand it in.")]
        [Min(30)] public float seconds = 180;
        [Tooltip("Up to five questions.")]
        public List<Question> questions = new List<Question>();
        [Tooltip("Offer the 5-4-3-2-1 grounding break (button, or B). It also opens by itself after two answers.")]
        public bool grounding = true;
        [Tooltip("The worried thought under the clock, before the grounding break.")]
        public string worry = "What if I can't finish?";
        [Tooltip("The thought under the clock after the grounding break.")]
        public string calm = "I'm here, in this room. I can return to the next question.";

        public int Count => Mathf.Min(MaxQuestions, questions.Count);
    }
}
