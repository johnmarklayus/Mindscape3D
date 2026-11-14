using System.Collections;
using UnityEngine;
using static Mindscape.AcademicPressure.StoryWords;

namespace Mindscape.AcademicPressure
{
    // Episode 2 · Classroom. The bus stops at the school gate; cross the yard to Room 03, hear the deadline announced, notice the comparison,
    // talk with a friend (three replies that converge), then take a breath with the breathing exercise.
    public sealed class ClassroomEpisode : AcademicEpisode
    {
        public Transform entrance, seat, seatView, teacher, classmate, friend, openingView, spawn, bus;
        public Transform landing;   // just inside Room 03's door, facing into the room
        public GameObject routeMarkers;
        public string friendName = "Sam";

        public override int Episode => 2;
        protected override float TimeLimit => 480;

        bool inside, seated, talked;
        Transform deskBag;

        protected override string RoamHint => !inside ? "Follow the blue markers through the gate to Room 03. Hold Shift to run." :
            !seated ? "Your seat has the gold marker." : "Your friend is waiting by the desks.";

        protected override IEnumerator Play()
        {
            // Room 03's door opens with its own [ E ]; walking in past it is what enters the classroom.
            AddArrival(landing != null ? landing : Waypoint("Inside Room 03", entrance.position + Vector3.ProjectOnPlane(seat.position - entrance.position, Vector3.up).normalized * 2.2f),
                W("Walk into your classroom"), () => !inside, EnterClassroom, 2.2f);
            AddSpot(seat, W("Take your seat"), () => inside && !seated, TakeSeat);
            AddSpot(friend, W("Talk to ") + friendName, () => seated && !talked, TalkToFriend, 3.6f);

            if (routeMarkers != null) routeMarkers.SetActive(false);
            // The bag beside your desk is the one you carry in: it only appears there once you have sat down.
            deskBag = transform.Find("Your school bag");
            if (deskBag != null) deskBag.gameObject.SetActive(false);
            if (openingView != null) Shot(openingView.position, openingView.position + openingView.forward * 10);
            player.gameObject.SetActive(false);
            yield return Card(W("Episode 02  ·  The Announcement"), W("Begin  [Space]"));
            // The bus pulls in at the stop outside the school gate.
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
            // From the sidewalk beside you (behind you is the bus), looking toward the gate.
            Shot(HomeWelcome.ClearView(spawn.position + Vector3.up * 2, spawn.position + spawn.right * 5 - spawn.forward * .5f + Vector3.up * 3), spawn.position + spawn.forward * 8 + Vector3.up * 1.5f);   // in front of the gate pillars
            yield return Fade(1, 0, .3f);
            if (bus != null) StartCoroutine(DriveOff());
            yield return Think(W("School. The gate is open and the yard is already busy.\nRoom 03 is across the yard, along the corridor."));
            if (routeMarkers != null) routeMarkers.SetActive(true);

            SetObjective(W("Go to your classroom"), Check(false, W("Room 03, across the yard  ·  hold Shift to run")));
            yield return RoamUntil(() => inside);
            SetObjective(W("Find your seat"), Check(true, W("Room 03")) + Check(false, W("Your seat")));
            yield return RoamUntil(() => seated);
            if (!talked)
            {
                SetObjective(W("Talk to your friend"), Check(false, friendName + W(" is by the desks")));
                yield return RoamUntil(() => talked);
            }

            Complete(W("The announcement"),
                W("The deadline was announced, and someone else is almost done.\n\n") +
                W("You talked with ") + friendName + W(" and ") + (Recall(AcademicPressureChapter.Breathing) == "completed" ? W("took a full breathing break.") : W("paused for a breath.")) +
                W("\n\nYour choices are saved."));
        }

        IEnumerator DriveOff()
        {
            for (float t = 0; t < 4; t += Time.deltaTime) { bus.position += Vector3.right * Time.deltaTime * (2 + t * 4); yield return null; }
            bus.gameObject.SetActive(false);
        }

        IEnumerator EnterClassroom()
        {
            if (routeMarkers != null) routeMarkers.SetActive(false);
            yield return Think(W("Everyone is already talking about their projects."));
            inside = true;
        }

        IEnumerator TakeSeat()
        {
            yield return Fade(0, 1, .3f);
            PlayerBackpack.Wear(player, false);   // the bag stays at the desk
            if (deskBag != null) deskBag.gameObject.SetActive(true);
            // Sitting at the desk (beside Sam) for the rest of the lesson; the class shots are from the seat.
            bool sitting = Chair(out var seatTop);
            if (sitting) SitAt(seatTop, Quaternion.LookRotation(Flat(seatView.forward)).eulerAngles.y);
            else player.gameObject.SetActive(false);
            Shot(seatView.position, seatView.position + seatView.forward * 6);
            yield return Fade(1, 0, .4f);

            if (teacher != null) yield return Glide(seatView.position, teacher.position + Vector3.up * 2.3f, 1.2f);
            yield return DialogueSequence(
                Say(W("Teacher"), W("Remember that your project presentation is tomorrow. Make sure your work is ready.")),
                Me(W("Tomorrow..."), () => AddStress(12)),
                BeforeDialogue(classmate != null ? Glide(seatView.position, classmate.position + Vector3.up * 1.4f, 1f) : null,
                    Say(W("Classmate"), W("I'm almost finished with mine. I just need to polish a few things."))),
                Think(W("They're already finished..."), () => AddStress(10)),
                // The morning's decision returns as a small change in the inner voice.
                Think(Recall(AcademicPressureChapter.LaptopPlan) == "one_task"
                    ? W("This morning I said I'd start with one part. I haven't started it yet.")
                    : W("This morning I told myself I'd finish everything tonight. Everything.")),
                BeforeDialogue(teacher != null ? Glide(seatView.position, teacher.position + Vector3.up * 2.3f, 1f) : null,
                    Say(W("Teacher"), W("That's all for this morning. Use your free period well."))));

            // Still in your seat: turn to Sam beside you and talk, then stand up.
            if (sitting)
            {
                yield return TalkToFriend();
                yield return Fade(0, 1, .3f);
                StandUpAt(new Vector3(seat.position.x, spawn.position.y, seat.position.z), Quaternion.LookRotation(Vector3.ProjectOnPlane(friend.position - seat.position, Vector3.up)).eulerAngles.y);
                yield return Fade(1, 0, .3f);
                seated = true;
                yield break;
            }
            yield return Fade(0, 1, .3f);
            player.gameObject.SetActive(true);
            Teleport(new Vector3(seat.position.x, spawn.position.y, seat.position.z),Quaternion.LookRotation(Vector3.ProjectOnPlane(friend.position - seat.position, Vector3.up)).eulerAngles.y);
            yield return Fade(1, 0, .3f);
            seated = true;
        }

        // Your chair: the classroom seat right under the seat view (the camera sits at your eyes when seated).
        bool Chair(out Vector3 top)
        {
            top = Vector3.zero;
            Renderer best = null; float bestD = 1.2f;
            foreach (var r in FindObjectsByType<Renderer>(FindObjectsSortMode.None))
            {
                if (!r.name.Contains("Wood_Seat") || !r.gameObject.activeInHierarchy) continue;
                Vector3 d = r.bounds.center - seatView.position; d.y = 0;
                if (d.magnitude < bestD) { bestD = d.magnitude; best = r; }
            }
            if (best == null) return false;
            top = new Vector3(best.bounds.center.x, best.bounds.max.y, best.bounds.center.z);
            return true;
        }

        static Vector3 Flat(Vector3 v) { v.y = 0; return v.sqrMagnitude < 1e-4f ? Vector3.forward : v.normalized; }

        // Sam from the front, a little to your side: the class faces the board, so a shot from where you stand only showed
        // the backs of heads. The camera stands between the desks in front of Sam, at head height, turned back toward them.
        void FriendShot()
        {
            var body = friend.parent != null ? friend.parent : friend;
            Vector3 face = Vector3.ProjectOnPlane(body.forward, Vector3.up).normalized;
            if (face.sqrMagnitude < .01f) { ShotOver(friend, 2.6f, 1.4f); return; }
            Vector3 side = Vector3.Cross(Vector3.up, face);
            if (Vector3.Dot(player.position - friend.position, side) < 0) side = -side;
            Shot(friend.position + face * 2.8f + side * 1.2f + Vector3.up * .45f, friend.position + Vector3.up * .05f);
        }

        IEnumerator TalkToFriend()
        {
            FriendShot();
            yield return Say(friendName, W("You look worried. Everything okay?"));
            int reply = 0;
            yield return Choose(friendName, W("What do you say?"), new[]
            {
                W("\"I'm fine.\""),
                W("\"I'm having a hard time keeping up.\""),
                W("\"I don't know if I can finish everything.\"")
            }, i => reply = i);
            Record(AcademicPressureChapter.FriendReply, reply == 0 ? "fine" : reply == 1 ? "hard_time" : "cannot_finish");
            EaseStress(reply == 0 ? 2 : 6);   // saying it out loud
            if (reply == 0) yield return Say(friendName, W("Okay. But if you need help, just let me know."));
            else if (reply == 1) yield return Say(friendName, W("You don't have to finish everything at once. What part are you working on?"));
            else yield return Say(friendName, W("Take it one step at a time. You can start with the part you understand."));

            // The three replies converge here.
            yield return Card(PlayerName + W(" feels overwhelmed."), W("Continue  [Space]"));
            yield return Card(W("Take a moment."), W("Continue  [Space]"));
            FriendShot();
            yield return Say(friendName, W("Let's slow down for a moment. Take a breath."));
            bool completed = false;
            yield return Breathe(done => completed = done);
            Record(AcademicPressureChapter.Breathing, completed ? "completed" : "closed_early");
            yield return DialogueSequence(
                completed ? Me(W("I feel a little calmer.")) : Me(W("A little slower. I can come back to the breath whenever I need it.")),
                Say(friendName, W("Let's get lunch later. The cafeteria fills up fast.")));
            talked = true;
        }
    }
}
