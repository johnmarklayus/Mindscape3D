using System.Collections;
using System.Linq;
using Mindscape.AcademicPressure;
using Mindscape.Minigames;
using UnityEngine;
using static Mindscape.AcademicPressure.StoryWords;

namespace Mindscape.FamilyExpectations
{
    // Episode 3 · Running Out of Time. The bus arrives at school after the examination has begun: cross the yard to
    // Room 03, speak to the teacher, find the empty seat, and answer what you can in the time that remains. A short
    // grounding break steadies the clock-watching; the paper is handed in as it is. No score is shown.
    public sealed class FamilyExamEpisode : FamilyEpisode
    {
        public Transform entrance, landing, seat, seatView, teacher, openingView, spawn, bus;
        public GameObject routeMarkers;
        [Min(30)] public float examinationSeconds = 180;

        public override int Episode => 3;
        protected override float TimeLimit => 420;
        protected override string FlashbackLabel => "Examination morning";

        [Tooltip("The examination paper (questions, time, grounding break). Empty: Resources/Story/Exams/Chapter 2 - Episode 3, or the built-in paper.")]
        public ExamPaper examPaper;

        bool admitted, seated, grounded;
        int answered;
        protected override string RoamHint => !admitted ? "Follow the blue markers across the yard to Room 03. Hold Shift to run." : "Find the empty seat with the gold marker.";

        Transform deskBag;

        protected override IEnumerator Play()
        {
            // The bag beside your desk is the one you carry in: it only appears there once you have sat down.
            deskBag = transform.Find("Your school bag");
            if (deskBag == null)
                foreach (var t in FindObjectsByType<Transform>(FindObjectsSortMode.None)) if (t.name == "Your school bag") { deskBag = t; break; }
            if (deskBag != null) deskBag.gameObject.SetActive(false);
            // Room 03's door opens with its own [ E ]; stepping inside is where the teacher speaks to you.
            AddArrival(landing != null ? landing : entrance, W("Enter Room 03"), () => !admitted, Admission, 2.2f);
            AddSpot(seat, W("Sit down and begin"), () => admitted && !seated, Sit);

            if (routeMarkers != null) routeMarkers.SetActive(false);
            if (openingView != null) Shot(openingView.position, openingView.position + openingView.forward * 10);
            player.gameObject.SetActive(false);
            yield return Card(TitleCard, W("Begin  [Space]"));
            if (bus != null)
            {
                Vector3 stopAt = bus.position, from = stopAt + Vector3.left * 45;
                bus.gameObject.SetActive(true);
                for (float t = 0; t < 3.5f; t += Time.deltaTime) { bus.position = Vector3.Lerp(from, stopAt, Mathf.SmoothStep(0, 1, t / 3.5f)); yield return null; }
                bus.position = stopAt;
            }
            yield return Fade(0, 1, .3f);
            player.gameObject.SetActive(true);
            Teleport(spawn.position, spawn.eulerAngles.y);
            PlayerBackpack.Wear(player, true);   // off the bus with the school bag, until the seat
            Shot(HomeWelcome.ClearView(spawn.position + Vector3.up * 2, spawn.position + spawn.right * 5 - spawn.forward * .5f + Vector3.up * 3), spawn.position + spawn.forward * 8 + Vector3.up * 1.5f);   // in front of the gate pillars
            yield return Fade(1, 0, .3f);
            if (bus != null) StartCoroutine(DriveOff());
            yield return Me(W("I'm here. I can't get those minutes back.\nI just need to reach my classroom."));
            AddStress(15);
            if (routeMarkers != null) routeMarkers.SetActive(true);

            SetObjective(W("Reach Room 03"), Check(false, W("Across the yard, along the corridor  ·  hold Shift to run")));
            yield return RoamUntil(() => admitted);
            SetObjective(W("Find your seat"), Check(true, W("Room 03")) + Check(false, W("The empty seat with the gold marker")));
            yield return RoamUntil(() => seated);

            yield return TakeExam(Paper(), r => { answered = r.answered; grounded = r.grounded; });

            yield return DialogueSequence(
                Say(W("Teacher"), W("Thank you, ") + PlayerName + W(". You can leave your paper here.")),
                Think(W("I did what I could with the time I had.\nI don't know how it will turn out yet.")),
                Think(W("But the thought follows me out of the room.\nWhat will my family say if it isn't enough?")));
            AddStress(8);
            Record("family.exam_answered", answered.ToString());
            Record("family.exam_grounding", grounded ? "taken" : "skipped");
            yield return Fade(0, 1, .7f);
            Complete(W("I used the time I had."),
                W("You arrived, found your place, and handed in your examination.\n\n") + answered + W(" of ") + Paper().Count + W(" questions answered. ") +
                (grounded ? W("You took a moment to steady yourself.") : W("You kept going at your own pace.")) + W("\n\nYour grade is still unknown."));
        }

        IEnumerator DriveOff()
        {
            for (float t = 0; t < 4; t += Time.deltaTime) { bus.position += Vector3.right * Time.deltaTime * (2 + t * 4); yield return null; }
            bus.gameObject.SetActive(false);
        }

        IEnumerator Admission()
        {
            if (routeMarkers != null) routeMarkers.SetActive(false);
            if (teacher != null)
            {
                Vector3 toTeacher = Vector3.ProjectOnPlane(teacher.position - player.position, Vector3.up).normalized;
                Shot(player.position - toTeacher * 2.6f + Vector3.up * 4.4f, teacher.position);
            }
            yield return DialogueSequence(
                Me(W("I'm sorry I'm late. May I still take the examination?")),
                Say(W("Teacher"), W("Come in quietly, ") + PlayerName + W(". Take the empty seat.\nStart with what you know and use the time that remains.")),
                Think(W("It feels like everyone noticed. They're looking at their papers now.\nOne step. Find my seat.")));
            AddStress(10);
            admitted = true;
        }

        IEnumerator Sit()
        {
            yield return Fade(0, 1, .3f);
            PlayerBackpack.Wear(player, false);   // the bag stays at the desk
            if (deskBag != null) deskBag.gameObject.SetActive(true);
            player.gameObject.SetActive(false);
            Shot(seatView.position, seatView.position + seatView.forward * 6);
            yield return Fade(1, 0, .4f);
            yield return Think(W("The words look familiar, but my thoughts keep racing.\nI'll begin with one question I understand."));
            seated = true;
        }

        // ---------------------------------------------------------------- the examination paper

        ExamPaper paper;

        // The paper: the field, else the asset in Resources, else the one this episode was written with.
        ExamPaper Paper()
        {
            if (paper != null) return paper;
            paper = examPaper != null ? examPaper : Resources.Load<ExamPaper>("Story/Exams/Chapter 2 - Episode 3");
            if (paper != null) return paper;
            paper = ScriptableObject.CreateInstance<ExamPaper>();
            paper.seconds = examinationSeconds;
            paper.questions = new System.Collections.Generic.List<ExamPaper.Question>
            {
                Q("A notebook costs 24 pesos. How much do three notebooks cost?", "48 pesos", "72 pesos", "96 pesos"),
                Q("Read: ‘Even though it rained, Ana brought the seedlings outside after the clouds cleared.’\n\nWhen did Ana bring the seedlings outside?", "Before the rain", "While it was raining", "After the clouds cleared"),
                Q("A bus travels 12 kilometers in 30 minutes. At the same speed, how far will it travel in one hour?", "18 kilometers", "24 kilometers", "36 kilometers"),
                Q("Which sentence is an observation rather than a prediction?", "The clock shows 8:15.", "Everyone will finish before me.", "This will be my worst examination."),
                Q("A class plants 40 seeds. Three-quarters of them sprout. How many seeds sprout?", "10 seeds", "20 seeds", "30 seeds"),
            };
            return paper;
        }

        static ExamPaper.Question Q(string question, params string[] answers) =>
            new ExamPaper.Question { question = question, answers = new System.Collections.Generic.List<string>(answers) };
    }
}
