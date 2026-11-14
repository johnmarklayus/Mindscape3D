using System;
using System.Collections;
using System.Linq;
using Mindscape.FamilyExpectations;
using Mindscape.Minigames;
using UnityEngine;
using UnityEngine.InputSystem;
using UIE = UnityEngine.UIElements;
using static UnityEngine.UIElements.UQueryExtensions;

namespace Mindscape.AcademicPressure
{
    // The minigames every episode can open, so a cinematic step (or one line of a script) plays them:
    //   * TakeExam: an examination paper (ExamPaper asset) with a clock and the 5-4-3-2-1 grounding break;
    //   * WorryCourtroom: a worry put on trial (WorryCourtroomCase asset, WorryCourtroom.prefab);
    //   * Practice: one of the practice minigames (Assets/Prefabs/Minigames: memory match, focus challenge…);
    //   * Talk: a Conversation asset as one dialogue.
    // The breathing exercise is Breathe (AcademicEpisode.cs).
    public abstract partial class AcademicEpisode
    {
        bool minigameOpen;

        // Story keys, pause and the HUD step aside while an episode's own overlay or one of these minigames is open.
        bool AnyOverlay => OverlayOpen || minigameOpen || examOpen;

        // ================================================================ a conversation asset

        /// <summary>Plays a Conversation asset as one dialogue (shared x / n counter).</summary>
        protected IEnumerator Talk(Conversation conversation)
        {
            if (conversation == null || conversation.lines.Count == 0) yield break;
            yield return DialogueSequence(conversation.lines.Select(l => Spoken(l.speaker, l.words)).ToArray());
        }

        // Who speaks, from a name typed in the Inspector: empty or "Narration", "Thought", "Joey" (the player), or a name.
        IEnumerator Spoken(string speaker, string text)
        {
            string who = (speaker ?? "").Trim(), words = Mindscape.Data.MindscapeDatabase.Personalize(text ?? "");
            string lower = who.ToLowerInvariant();
            if (who == "" || lower == "narration" || lower == "narrator") return Say("Narration", words);
            if (lower == "thought" || lower == "think" || lower == "thinking") return Think(words);
            if (lower == "joey" || lower == "me" || lower == "player" || who == PlayerName) return Me(words);
            return Say(who, words);
        }

        // ================================================================ the Worry Courtroom

        /// <summary>Puts a worry on trial. Gives back the balanced thought the player reached (or the case's own).</summary>
        protected IEnumerator WorryCourtroom(GameObject prefab, WorryCourtroomCase worry, Action<string, string> finished)
        {
            // A loaded save skips the trial and keeps the thought reached the first time.
            if (ReplayNext('k', out var kept)) { yield return null; finished?.Invoke(kept, ""); yield break; }
            var court = prefab != null ? Instantiate(prefab, transform).GetComponent<WorryCourtroomMinigame>() : null;
            if (court == null || worry == null)
            {
                Debug.LogWarning("[" + name + "] Worry Courtroom step: set the Case (and the Minigame prefab, Assets/Prefabs/Minigames/WorryCourtroom.prefab).");
                if (court != null) Destroy(court.gameObject);
                finished?.Invoke("", ""); yield break;
            }
            court.name = "Worry Courtroom";
            court.startOpen = false;
            court.cases = new System.Collections.Generic.List<WorryCourtroomCase> { worry }; court.startCase = 0;
            yield return null; yield return null;   // its Start wires the buttons and hides the screen
            yield return Fade(fadeAlpha, 1, .4f);
            HidePanels(); SetLocked(true); minigameOpen = true;
            court.Open(null);
            yield return Fade(1, 0, .2f);
            while (court.IsOpen) yield return null;
            minigameOpen = false;
            string thought = court.BalancedThought ?? "", step = court.SmallStep ?? "";
            Log('k', thought);
            Destroy(court.gameObject);
            SetLocked(true);
            finished?.Invoke(thought, step);
        }

        // ================================================================ a practice minigame

        /// <summary>Opens a practice minigame (a prefab with a MinigamePopup) and waits for the player to close it.</summary>
        protected IEnumerator Practice(GameObject prefab, Action<bool> finished)
        {
            if (ReplayNext('p', out var kept)) { yield return null; finished?.Invoke(kept == "1"); yield break; }
            var game = prefab != null ? Instantiate(prefab, transform).GetComponent<MinigamePopup>() : null;
            if (game == null)
            {
                Debug.LogWarning("[" + name + "] Practice minigame step: set the Minigame (a prefab from Assets/Prefabs/Minigames).");
                finished?.Invoke(false); yield break;
            }
            yield return null;
            HidePanels(); SetLocked(true); minigameOpen = true;
            bool completed = false;
            game.onCompleted.AddListener(() => completed = true);
            game.Open();
            while (game.IsOpen) yield return null;
            minigameOpen = false;
            Log('p', completed ? "1" : "0");
            Destroy(game.gameObject);
            SetLocked(true);
            if (completed) EaseStress(10);
            finished?.Invoke(completed);
        }

        // ================================================================ the examination paper

        public struct ExamResult { public int answered; public int[] answers; public bool grounded; }

        // The 5-4-3-2-1 grounding technique: five things you see, four you feel, three you hear, two you smell, one you taste.
        static readonly string[] GroundingSense = { "5  ·  SEE", "4  ·  TOUCH", "3  ·  HEAR", "2  ·  SMELL", "1  ·  TASTE" };
        static readonly string[] GroundingWords =
        {
            "Look around the room. Tap five things you can see.",
            "Now tap four things you can feel or touch.",
            "Listen. Tap three things you can hear.",
            "Tap two things you can smell.",
            "Tap one thing you can taste."
        };
        static readonly string[] GroundingActions = { "I see five things", "I feel four things", "I hear three sounds", "I smell two things", "I notice one taste" };
        static readonly string[] GroundingVerb = { "see", "feel", "hear", "smell", "taste" };
        // The pictures in the grounding break: things in a classroom and on you. Senses: 1 see, 2 touch, 4 hear, 8 smell, 16 taste.
        static readonly (string kind, string label, int senses)[] GroundingItems =
        {
            ("desk", "The desk", 1 | 2), ("paper", "Your paper", 1 | 2 | 4 | 8), ("pencil", "Your pencil", 1 | 2 | 4 | 8),
            ("window", "The window", 1 | 4), ("clock", "The clock", 1 | 4), ("chair", "Your chair", 1 | 2),
            ("feet", "Feet on the floor", 2), ("water", "Water bottle", 1 | 2 | 16), ("fan", "The ceiling fan", 1 | 2 | 4),
            ("board", "The chalkboard", 1 | 8), ("breath", "Your breathing", 4 | 8 | 16), ("sleeves", "Your sleeves", 2 | 8),
        };
        static readonly string[] GroundingFound = { "I can see it.", "I can feel it.", "I can hear it.", "I can smell it.", "I can taste it." };

        ExamPaper exam;
        bool examOpen, examSubmitted, groundingOpen, confirmOpen, examGrounded, timeUp;
        int[] examAnswers; bool[] examFlagged;
        int examSelected, groundingStep, groundingFound;
        readonly bool[] groundingPicked = new bool[GroundingItems.Length];
        UIE.Button[] groundingTiles;
        UIE.Label groundingStatus;
        float examRemaining, groundingAt, tickAt;
        // The paper, the grounding break and the hand-in prompt are one UI Toolkit file (ExamPaper.uxml).
        UIE.VisualElement examRoot, examScreen, groundingScreen, confirmScreen;
        UIE.Label examClock, examThought, examQuestion, examProgress, groundingText, groundingCount, confirmationText;
        UIE.Button[] questionButtons, answerButtons;
        UIE.Button flagButton, groundingButton, groundButton;
        AudioClip examTick, examPage, examBell;

        int ExamCount => exam != null ? exam.Count : 0;
        int Answered => examAnswers == null ? 0 : examAnswers.Count(a => a >= 0);

        /// <summary>
        /// The examination paper: the player answers what they can before the clock runs out and hands it in. A loaded
        /// save hands it in again with the answers kept the first time.
        /// </summary>
        protected IEnumerator TakeExam(ExamPaper paper, Action<ExamResult> finished)
        {
            exam = paper;
            int count = ExamCount;
            examAnswers = Enumerable.Repeat(-1, count).ToArray(); examFlagged = new bool[count];
            examGrounded = timeUp = examSubmitted = false; examSelected = 0;
            if (ReplayNext('x', out var kept))
            {
                var parts = kept.Split(',');
                for (int i = 0; i < count && i < parts.Length - 1; i++) examAnswers[i] = int.Parse(parts[i]);
                examGrounded = parts[parts.Length - 1] == "1";
                yield return null;
                finished?.Invoke(Result()); yield break;
            }
            if (count == 0) { Debug.LogWarning("[" + name + "] Exam step: the exam paper has no questions."); finished?.Invoke(Result()); yield break; }
            SetLocked(true); HidePanels();
            BuildExam();
            examRemaining = paper.seconds;
            examOpen = true; Show(examRoot, true); DrawExam();
            while (!examSubmitted) yield return null;
            Show(examRoot, false); examOpen = false;
            effects.PlayOneShot(examPage, .15f);
            Log('x', string.Join(",", examAnswers) + "," + (examGrounded ? "1" : "0"));
            finished?.Invoke(Result());
        }

        ExamResult Result() => new ExamResult { answered = Answered, answers = examAnswers, grounded = examGrounded };

        // Called from Update while the paper is open (story keys are off then).
        void UpdateExam()
        {
            var k = Keyboard.current;
            if (groundingOpen)
            {
                groundingButton.SetEnabled(GroundingStepDone);
                if (k != null && k.spaceKey.wasPressedThisFrame) Ground();
                return;
            }
            if (confirmOpen) { if (k != null && k.escapeKey.wasPressedThisFrame) CancelSubmit(); return; }
            if (!timeUp)
            {
                examRemaining = Mathf.Max(0, examRemaining - Time.deltaTime);
                if (examRemaining < 60 && !examGrounded) AddStress(Time.deltaTime * .3f);
                if (examRemaining <= 0) { timeUp = true; effects.PlayOneShot(examBell, .12f); }
            }
            if (Time.time > tickAt) { effects.PlayOneShot(examTick, .035f); tickAt = Time.time + 1; }
            DrawClock();
            if (k == null) return;
            if (k.digit1Key.wasPressedThisFrame) Answer(0);
            if (k.digit2Key.wasPressedThisFrame) Answer(1);
            if (k.digit3Key.wasPressedThisFrame) Answer(2);
            if (k.leftArrowKey.wasPressedThisFrame) Select((examSelected + ExamCount - 1) % ExamCount);
            if (k.rightArrowKey.wasPressedThisFrame) Select((examSelected + 1) % ExamCount);
            if (k.bKey.wasPressedThisFrame) BeginGrounding();
        }

        string[] AnswersOf(int q)
        {
            var list = exam.questions[q].answers;
            var result = new string[ExamPaper.MaxAnswers];
            for (int i = 0; i < result.Length; i++) result[i] = i < list.Count ? list[i] ?? "" : "";
            return result;
        }

        void Select(int index) { if (groundingOpen || confirmOpen) return; examSelected = index; effects.PlayOneShot(examPage, .06f); DrawExam(); }

        void Answer(int option)
        {
            if (groundingOpen || confirmOpen || string.IsNullOrWhiteSpace(AnswersOf(examSelected)[option])) return;
            examAnswers[examSelected] = option; DrawExam();
            if (Answered >= 2 && !examGrounded) BeginGrounding();
        }

        void Flag() { if (groundingOpen || confirmOpen) return; examFlagged[examSelected] = !examFlagged[examSelected]; DrawExam(); }

        void BeginGrounding()
        {
            if (groundingOpen || confirmOpen || !exam.grounding) return;
            groundingOpen = true; groundingStep = 0; groundingAt = Time.time;
            examScreen.style.opacity = .25f; examScreen.SetEnabled(false);
            Show(groundingScreen, true); DrawGrounding();
        }

        int GroundingNeeded => 5 - groundingStep;
        bool GroundingStepDone => groundingFound >= GroundingNeeded && Time.time - groundingAt >= .4f;

        // A picture tapped: it counts when it fits the sense of this step (each picture once per step).
        void PickGrounding(int index)
        {
            if (!groundingOpen || groundingPicked[index] || groundingFound >= GroundingNeeded) return;
            var tile = groundingTiles[index];
            if ((GroundingItems[index].senses & (1 << groundingStep)) == 0)
            {
                groundingStatus.text = "Hmm, can you " + GroundingVerb[groundingStep] + " that? Try another one.";
                tile.AddToClassList("wrong");
                tile.schedule.Execute(() => tile.RemoveFromClassList("wrong")).StartingIn(600);
                return;
            }
            groundingPicked[index] = true; groundingFound++;
            tile.AddToClassList("found");
            effects.PlayOneShot(examPage, .08f);
            EaseStress(1);
            groundingAt = Time.time;
            groundingStatus.text = GroundingItems[index].label + ". " + GroundingFound[groundingStep] + "   " + groundingFound + " of " + GroundingNeeded;
        }

        void Ground()
        {
            if (!groundingOpen || !GroundingStepDone) return;
            groundingStep++; groundingAt = Time.time;
            EaseStress(3);
            if (groundingStep < GroundingWords.Length) { DrawGrounding(); return; }
            examGrounded = true; groundingOpen = false;
            Show(groundingScreen, false); examScreen.style.opacity = 1; examScreen.SetEnabled(true); DrawExam();
        }

        void RequestSubmit()
        {
            if (groundingOpen) return;
            confirmOpen = true; examScreen.SetEnabled(false); Show(confirmScreen, true);
            confirmationText.text = Answered + " of " + ExamCount + " questions answered.\nYou may hand in your work as it is, or return to the paper.";
        }

        void CancelSubmit() { confirmOpen = false; Show(confirmScreen, false); examScreen.SetEnabled(true); }
        void Submit() { if (!confirmOpen) return; confirmOpen = false; Show(confirmScreen, false); examSubmitted = true; }

        static void Show(UIE.VisualElement element, bool on) => element.EnableInClassList("hidden", !on);

        void DrawGrounding()
        {
            groundingCount.text = "5-4-3-2-1 GROUNDING  /  " + GroundingSense[groundingStep] + "  /  STEP " + (groundingStep + 1) + " OF " + GroundingWords.Length;
            groundingText.text = GroundingWords[groundingStep];
            groundingButton.text = (groundingStep == GroundingWords.Length - 1 ? "I'm here. Back to the paper" : GroundingActions[groundingStep]) + "  [Space]";
            groundingButton.SetEnabled(false);
            groundingFound = 0;
            for (int i = 0; i < groundingTiles.Length; i++) { groundingPicked[i] = false; groundingTiles[i].RemoveFromClassList("found"); groundingTiles[i].RemoveFromClassList("wrong"); }
            groundingStatus.text = "0 of " + GroundingNeeded + "  ·  take your time";
        }

        void DrawClock()
        {
            int s = Mathf.CeilToInt(examRemaining);
            examClock.text = timeUp ? "TIME'S UP  /  WRAP UP" : (s / 60).ToString("00") + ":" + (s % 60).ToString("00") + "  REMAINING";
            examThought.text = timeUp ? "The bell has rung. Finish your thought, then hand in your paper." :
                examGrounded ? exam.calm : exam.grounding ? exam.worry + "  ·  Press B for a 5-4-3-2-1 grounding break." : exam.worry;
        }

        void DrawExam()
        {
            DrawClock();
            int count = ExamCount;
            examQuestion.text = Mindscape.Data.MindscapeDatabase.Personalize(exam.questions[examSelected].question);
            examProgress.text = "QUESTION " + (examSelected + 1).ToString("00") + "   /   " + Answered + " OF " + count + " ANSWERED";
            for (int i = 0; i < questionButtons.Length; i++)
            {
                questionButtons[i].style.display = i < count ? UIE.DisplayStyle.Flex : UIE.DisplayStyle.None;
                if (i >= count) continue;
                questionButtons[i].EnableInClassList("selected", i == examSelected);
                questionButtons[i].text = (i + 1).ToString("00") + (examAnswers[i] >= 0 ? "  DONE" : "  —") + (examFlagged[i] ? "  •" : "");
            }
            var options = AnswersOf(examSelected);
            for (int i = 0; i < answerButtons.Length; i++)
            {
                bool used = !string.IsNullOrWhiteSpace(options[i]);
                answerButtons[i].style.display = used ? UIE.DisplayStyle.Flex : UIE.DisplayStyle.None;
                answerButtons[i].EnableInClassList("selected", examAnswers[examSelected] == i);
                answerButtons[i].text = (i + 1) + "   " + options[i] + (examAnswers[examSelected] == i ? "  [selected]" : "");
            }
            flagButton.text = examFlagged[examSelected] ? "Remove review mark" : "Mark for review";
            if (groundButton != null) groundButton.style.display = exam.grounding ? UIE.DisplayStyle.Flex : UIE.DisplayStyle.None;
        }

        void BuildExam()
        {
            if (examRoot != null) return;
            examTick = Tone("Classroom clock", 1100, .045f); examPage = Tone("Paper", 180, .16f); examBell = Tone("School bell", 660, 1.3f);
            examRoot = Overlay(EpisodeUI.Load().examPaper, "examination").Q("exam-root");
            examScreen = examRoot.Q("exam-screen"); groundingScreen = examRoot.Q("grounding-screen"); confirmScreen = examRoot.Q("confirm-screen");
            examClock = examRoot.Q<UIE.Label>("exam-clock"); examThought = examRoot.Q<UIE.Label>("exam-thought");
            examProgress = examRoot.Q<UIE.Label>("exam-progress"); examQuestion = examRoot.Q<UIE.Label>("exam-question");
            questionButtons = new UIE.Button[ExamPaper.MaxQuestions]; answerButtons = new UIE.Button[ExamPaper.MaxAnswers];
            for (int i = 0; i < questionButtons.Length; i++) { int q = i; questionButtons[i] = examRoot.Q<UIE.Button>("exam-q-" + i); questionButtons[i].clicked += () => Select(q); }
            for (int i = 0; i < answerButtons.Length; i++) { int option = i; answerButtons[i] = examRoot.Q<UIE.Button>("exam-a-" + i); answerButtons[i].clicked += () => Answer(option); }
            flagButton = examRoot.Q<UIE.Button>("exam-flag"); flagButton.clicked += Flag;
            groundButton = examRoot.Q<UIE.Button>("exam-ground"); groundButton.clicked += BeginGrounding;
            examRoot.Q<UIE.Button>("exam-submit").clicked += RequestSubmit;
            groundingCount = examRoot.Q<UIE.Label>("ground-count"); groundingText = examRoot.Q<UIE.Label>("ground-text");
            groundingButton = examRoot.Q<UIE.Button>("ground-button"); groundingButton.clicked += Ground;
            groundingStatus = examRoot.Q<UIE.Label>("ground-status");
            var tiles = examRoot.Q("ground-items");
            groundingTiles = new UIE.Button[GroundingItems.Length];
            for (int i = 0; i < GroundingItems.Length; i++)
            {
                int index = i;
                var tile = new UIE.Button(() => PickGrounding(index)) { text = "" };
                tile.AddToClassList("ground-item");
                var icon = new GroundingIcon(GroundingItems[i].kind); icon.AddToClassList("ground-icon");
                var label = new UIE.Label(GroundingItems[i].label) { pickingMode = UIE.PickingMode.Ignore }; label.AddToClassList("ground-label");
                tile.Add(icon); tile.Add(label);
                tiles.Add(tile);
                groundingTiles[i] = tile;
            }
            confirmationText = examRoot.Q<UIE.Label>("confirm-text");
            examRoot.Q<UIE.Button>("confirm-back").clicked += CancelSubmit;
            examRoot.Q<UIE.Button>("confirm-ok").clicked += Submit;
            // Space and Enter belong to the story and the grounding break; a focused button would also "click" on them.
            examRoot.Query<UIE.Button>().ForEach(b => b.focusable = false);
            Show(examRoot, false); Show(groundingScreen, false); Show(confirmScreen, false);
        }
    }
}
