using System.Collections;
using System.Linq;
using Mindscape.Data;
using UnityEngine;
using UIE = UnityEngine.UIElements;
using static UnityEngine.UIElements.UQueryExtensions;

namespace Mindscape.AcademicPressure
{
    // Episode 1 · House. Wake up to reminders of school: the phone's deadline and the unfinished project (first decision
    // + thought identification). Then the morning, in order: make the bed, eat breakfast and wash the plate, shower and
    // change into the uniform, pick up the school bag and go outside; then the walk to the bus stop.
    public sealed class HouseEpisode : AcademicEpisode
    {
        public Transform phone, laptop, books, schoolBag, bed, plate, sink, frontDoor, busStop, bus;
        public GameObject messyBed, fixedBed, carriedBag, carriedPlate, routeMarkers, laptopScreen;
        public Vector3 outsideSpawn = new Vector3(-22.1f, .7f, 8.2f);
        public float outsideYaw = 0;

        public override int Episode => 1;
        protected override bool AsksForName => true;
        protected override float TimeLimit => 720;

        bool phoneChecked, laptopChecked, bagPacked, bedMade, plateCleared, plateWashed, dressed, leftHouse, atStop;
        AudioClip alarm;

        protected override string RoamHint => !phoneChecked ? "Your phone is on the bedside table." :
            !laptopChecked ? "Your laptop is on the desk." :
            !bedMade ? "First, make your bed." :
            !plateCleared ? "Breakfast is on the dining table." :
            !plateWashed ? "Wash your plate at the kitchen sink." :
            !dressed ? "The bathroom is down the hall. Take a shower and change into your school uniform there." :
            !bagPacked ? "Your school bag is in your room." :
            !leftHouse ? "The front door is in the living room. Open it and step outside." : "Follow the blue markers to the bus stop.";

        // The morning's four steps, ticked off as they are done.
        string Morning() =>
            Check(bedMade, "Make your bed") +
            Check(plateWashed, !plateCleared ? "Eat breakfast at the dining table" : "Wash your plate at the kitchen sink") +
            Check(dressed, "Shower and change into your uniform") +
            Check(leftHouse, !bagPacked ? "Pick up your school bag" : "Go outside through the front door");

        protected override IEnumerator Play()
        {
            alarm = Tone("Morning alarm", 760, 1.6f, true);
            if (messyBed != null) messyBed.SetActive(true);
            if (fixedBed != null) fixedBed.SetActive(false);
            if (carriedBag != null) carriedBag.SetActive(false);
            if (carriedPlate != null) carriedPlate.SetActive(false);
            if (routeMarkers != null) routeMarkers.SetActive(false);
            if (bus != null) bus.gameObject.SetActive(false);

            AddSpot(phone, "Check your phone", () => !phoneChecked, CheckPhone);
            AddSpot(laptop, "Open your laptop", () => phoneChecked && !laptopChecked, OpenLaptop);
            // 1. The bed.
            AddSpot(bed, "Make your bed", () => laptopChecked && !bedMade, MakeBed, 3.6f);
            // 2. Breakfast, then the plate to the sink.
            AddSpot(plate, "Eat breakfast", () => bedMade && !plateCleared, EatBreakfast);
            AddSpot(sink, "Wash the plate", () => plateCleared && !plateWashed, WashPlate, 3.6f);
            // 3. Into the bathroom: a shower and the school uniform (a house without one skips the step).
            dressed = AddBathroom("Take a shower and change into your uniform", () => plateWashed && !dressed, Outfit.SchoolUniform,
                "A quick shower, then the uniform. Now I look ready, even if I don't feel it.", () => dressed = true) == null;
            // 4. The bag (the books go in with it), then out of the front door. The door opens with its own [ E ];
            // stepping out onto the path is what leaves the house.
            AddSpot(schoolBag, "Pick up your school bag", () => dressed && !bagPacked, PackBag);
            AddArrival(Waypoint("Outside the front door", outsideSpawn), "Leave for school", () => bagPacked && !leftHouse, LeaveHouse);
            AddSpot(busStop, "Wait for the bus", () => leftHouse && !atStop, WaitForBus, 4.5f);
            GuardBedroomDoor();

            // Opening: who is this story about? Joey is still in bed when the alarm goes off.
            float tall = PlayerHeight();
            bool lying = LieInBed(out var pillowEnd, out var headward);
            Vector3 face = lying ? pillowEnd + headward * tall * .38f + Vector3.up * .3f : bed.position;
            // Joey's bed model (BedStates) shows the character asleep: frame the bed, then glide in close to the face.
            var beds = BedStates.InScene();
            bool sleeper = lying && beds != null && beds.Face(headward, out face);
            Shot(bed.position + new Vector3(-3.2f, 3.4f, 3.6f), sleeper ? beds.Top : bed.position);
            yield return Card("CHAPTER 1  ·  ACADEMIC PRESSURE\n<size=60%>Episode 01  ·  Tomorrow Already?</size>", "Begin  [Space]");
            // Signed in, the story uses your account username; only offline play asks for a name.
            if (MindscapeCloud.HasAccount) SkipKept('a');   // a save made back when this asked even when signed in
            else
            {
                string chosen = PlayerName;
                yield return Ask("Before we begin", "What name should the story use for you?", "Your name", MindscapeDatabase.HasPlayerName ? PlayerName : "", false, 24, "Start", n => chosen = n);
                MindscapeDatabase.PlayerName = chosen;
            }
            PlayerName = MindscapeDatabase.PlayerName;

            effects.clip = alarm; effects.loop = true; effects.volume = .14f; effects.Play();
            Vector3 closeUp = sleeper
                ? face - headward * 1.9f + Vector3.up * 2.0f + Vector3.Cross(Vector3.up, headward) * 1.3f
                : bed.position + new Vector3(-2.4f, 2.6f, 2.4f);
            yield return Glide(closeUp, lying ? face : bed.position + Vector3.up * .4f, 2.2f);
            yield return DialogueSequence(
                Say("Morning", "An alarm. The room is still half dark.", () => { effects.Stop(); effects.loop = false; }),
                Think("Morning already.\nBefore anything else, I should check my phone."));
            if (lying)
            {
                // Up and out of bed, standing beside it.
                yield return Fade(0, 1, .35f);
                GetUp();
                yield return Fade(1, 0, .35f);
            }

            SetObjective("Check your phone", Check(false, "Phone on the bedside table"));
            yield return RoamUntil(() => phoneChecked);

            SetObjective("Look at your project", Check(true, "Phone") + Check(false, "Laptop on the desk"));
            yield return RoamUntil(() => laptopChecked);

            yield return Think("Before I go, there are a few things to do.\nBed, breakfast, a shower, then my bag.");
            yield return RoamUntil(() =>
            {
                SetObjective("Get ready for school", Morning());
                return leftHouse;
            });

            SetObjective("Walk to the bus stop", Check(false, "Follow the blue markers"));
            yield return RoamUntil(() => atStop);

            string plan = Recall(AcademicPressureChapter.LaptopPlan) == "one_task" ? "You decided to start with one task first." : "You decided to finish everything tonight.";
            Complete("Tomorrow already?",
                "The reminder, the unfinished introduction, and a full morning.\n\n" + plan +
                "\nYou named a feeling: " + Recall(AcademicPressureChapter.Feeling, "—") + ".\n\nYour choices are saved.");
        }

        // ---------------------------------------------------------------- the bedroom door
        // The phone, the laptop and the bed are all in Joey's room. Until they are done, stepping out through the bedroom
        // door stops Joey with a reminder of what is left, and he turns back into the room.
        Vector3 roomSide; float roomYaw;

        void GuardBedroomDoor()
        {
            var door = FindObjectsByType<DoorInteraction>(FindObjectsSortMode.None).FirstOrDefault(d => d.name == "Door_Bedroom_Left" && d.isActiveAndEnabled);
            if (door == null || door.leaves == null || door.leaves.Length == 0 || bed == null) return;
            var b = door.leaves[0].bounds; foreach (var leaf in door.leaves) b.Encapsulate(leaf.bounds);
            Vector3 across = b.size.x < b.size.z ? Vector3.right : Vector3.forward;
            Vector3 outward = Vector3.Dot(b.center - bed.position, across) >= 0 ? across : -across;   // away from the bed
            Vector3 floor = new Vector3(b.center.x, b.min.y, b.center.z);
            roomSide = floor - outward * 1.8f;
            roomYaw = Quaternion.LookRotation(-outward).eulerAngles.y;
            var guard = AddArrival(Waypoint("Bedroom doorway (room not done)", floor + outward * 1.4f), "Leave your room", () => !bedMade, NotYet, 1.5f);
            if (guard.marker != null) { Destroy(guard.marker); guard.marker = null; }   // a reminder, not a goal: no marker
        }

        IEnumerator NotYet()
        {
            string left = !phoneChecked ? "check my phone" : !laptopChecked ? "look at my project on the laptop" : "make my bed";
            yield return Think("Not yet. I should finish things in my room first.\nI still need to " + left + ".");
            Teleport(roomSide, roomYaw);
        }

        // ---------------------------------------------------------------- interactions

        IEnumerator CheckPhone()
        {
            ShotOver(phone, 1.6f, 1.2f);
            OpenPhoneLock("7:12", "Monday");
            PhoneNotification("Reminder", "Research Project Submission", "Tomorrow  —  11:59 PM");
            yield return DialogueSequence(
                Think("Tomorrow already?"),
                Think("I knew it was close. Seeing the date makes it feel closer."),
                Think("There's still so much left to do on it.\nIt feels like the whole day is already counting down."));
            AddStress(12);
            ClosePhone();
            phoneChecked = true;
        }

        IEnumerator OpenLaptop()
        {
            ShotOver(laptop, 1.7f, 1.1f);
            if (laptopScreen != null) laptopScreen.SetActive(true);
            ShowLaptopDocument(true);
            yield return Me("I haven't even finished the first part.");
            ShowLaptopDocument(false);   // the decision gets the whole view
            int plan = 0;
            yield return Choose("Decision", "What will you do?", new[] { "\"I'll finish everything tonight.\"", "\"I'll start with one task first.\"" }, i => plan = i);
            Record(AcademicPressureChapter.LaptopPlan, plan == 0 ? "finish_everything" : "one_task");
            yield return plan == 0 ? Me("I have to finish everything tonight. I can't fall behind.") : Me("Maybe I should just start with one part.");

            // First CBT feature: thought identification.
            yield return Card("\"What if I fail this project?\"", "A thought appears  ·  Continue  [Space]");
            AddStress(10);
            string[] feelings = { "Worried", "Overwhelmed", "Frustrated", "Calm" };
            int felt = 0;
            yield return Choose("Thought identification", "What are you feeling?", feelings, i => felt = i);
            Record(AcademicPressureChapter.Feeling, feelings[felt]);
            EaseStress(6);   // naming the feeling
            yield return Think(felt == 3
                ? "Calm. The deadline is still there, and I can notice it without rushing."
                : feelings[felt] + ". That's what this feels like right now.\nNoticing it doesn't change the deadline, but it helps me see what's happening.");
            if (laptopScreen != null) laptopScreen.SetActive(false);
            laptopChecked = true;
        }

        // The laptop up close: the same laptop screen as Chapter 1 · Episode 4 (LaptopTasks.uxml), showing the project as a
        // document window with its three parts instead of the task list.
        UIE.VisualElement laptopDocument;

        void ShowLaptopDocument(bool show)
        {
            if (laptopDocument == null)
            {
                if (!show) return;
                laptopDocument = Overlay(EpisodeUI.Load().laptopTasks, "laptop project").Q("laptop-root");
                // Smaller than the task list so the whole laptop sits above the dialogue bar.
                var lap = laptopDocument.Q(className: "laptop");
                lap.style.transformOrigin = new UIE.TransformOrigin(UIE.Length.Percent(50), UIE.Length.Percent(0));
                lap.style.scale = new UIE.Scale(new Vector3(.76f, .76f, 1));
                laptopDocument.Q<UIE.Label>(className: "menubar-app").text = "Documents";
                laptopDocument.Q<UIE.Label>(className: "titlebar-title").text = "Research Project.docx";
                laptopDocument.Q(className: "removed").style.display = UIE.DisplayStyle.None;
                laptopDocument.Q<UIE.Label>(className: "window-title").text = "Research Project  ·  Draft";
                laptopDocument.Q(className: "laptop-start").style.display = UIE.DisplayStyle.None;
                laptopDocument.Q<UIE.Label>("laptop-status").text = "Due tomorrow.  Only the first part has been started.";
                laptopDocument.Q<UIE.Label>("laptop-status").style.width = UIE.Length.Percent(100);
                laptopDocument.Q("laptop-progress").style.width = UIE.Length.Percent(12);
                var list = laptopDocument.Q("laptop-tasks"); list.Clear();
                foreach (var (part, note) in new[] { ("1. Introduction", "unfinished"), ("2. References", "not started"), ("3. Slides", "not started") })
                {
                    var row = new UIE.VisualElement { pickingMode = UIE.PickingMode.Ignore };
                    row.AddToClassList("task");
                    var check = new UIE.VisualElement(); check.AddToClassList("check");
                    var tick = new UIE.VisualElement(); tick.AddToClassList("tick"); check.Add(tick);
                    var label = new UIE.Label(part + "   ·  " + note); label.AddToClassList("task-label");
                    row.Add(check); row.Add(label); list.Add(row);
                }
            }
            laptopDocument.EnableInClassList("hidden", !show);
        }

        IEnumerator PackBag()
        {
            ShotOver(schoolBag, 2f, 1.3f);
            yield return Think("ID, notebook, charger, my reference books. Everything for the day goes in here.");
            if (books != null) books.gameObject.SetActive(false);
            schoolBag.gameObject.SetActive(false);
            // Worn on the back from here (the old carried box stays hidden).
            PlayerBackpack.Wear(player, true);
            effects.PlayOneShot(chime, .1f);
            bagPacked = true;
        }

        IEnumerator MakeBed()
        {
            yield return Fade(0, 1, .3f);
            if (messyBed != null) messyBed.SetActive(false);
            if (fixedBed != null) fixedBed.SetActive(true);
            var beds = BedStates.InScene();
            if (beds != null)
            {
                // The whole bed, from the player's side, centred on the mattress (the story's bed pivot is at its foot).
                Vector3 top = beds.Top, from = Vector3.ProjectOnPlane(player.position - top, Vector3.up);
                if (from.sqrMagnitude < .01f) from = -player.forward;
                Shot(top + from.normalized * 3.4f + Vector3.up * 2.6f, top);
            }
            else ShotOver(bed, 3.2f, 2.4f);
            yield return Fade(1, 0, .3f);
            yield return Think("Pillow, blanket, done. One small thing finished.");
            EaseStress(4);
            bedMade = true;
        }

        IEnumerator EatBreakfast()
        {
            ShotOver(plate, 1.8f, 1.3f);
            yield return Think("Breakfast first. I should eat something before a long day.");
            yield return Fade(0, 1, .35f);
            plate.gameObject.SetActive(false);
            if (carriedPlate != null) carriedPlate.SetActive(true);
            yield return Fade(1, 0, .35f);
            yield return Think("That's better. Now the plate goes to the sink in the kitchen.");
            EaseStress(3);
            plateCleared = true;
        }

        IEnumerator WashPlate()
        {
            ShotOver(sink, 2.2f, 1.6f);
            yield return Fade(0, 1, .3f);
            if (carriedPlate != null) carriedPlate.SetActive(false);
            yield return Fade(1, 0, .3f);
            yield return Think("Washed and drying. The kitchen is quiet again.");
            plateWashed = true;
        }

        IEnumerator LeaveHouse()
        {
            if (routeMarkers != null) routeMarkers.SetActive(true);
            yield return Think("Fresh air. The bus stop is just down the street.");
            leftHouse = true;
        }

        IEnumerator WaitForBus()
        {
            atStop = true;
            if (routeMarkers != null) routeMarkers.SetActive(false);
            Shot(busStop.position + new Vector3(-6, 3.5f, -6), busStop.position + Vector3.up);
            yield return Think("The reminder keeps replaying in my head.\nTomorrow, 11:59 PM.");
            if (bus == null) yield break;
            // The trip to school: the bus pulls in, picks you up, and drives on.
            Vector3 stopAt = bus.position;
            bus.gameObject.SetActive(true);
            Vector3 from = stopAt + Vector3.left * 30;
            for (float t = 0; t < 3; t += Time.deltaTime) { bus.position = Vector3.Lerp(from, stopAt, Mathf.SmoothStep(0, 1, t / 3)); yield return null; }
            yield return Fade(0, 1, .35f);
            player.gameObject.SetActive(false);
            Shot(stopAt + new Vector3(4, 6, -14), stopAt + Vector3.up * 1.5f);
            yield return Fade(1, 0, .35f);
            for (float t = 0; t < 4; t += Time.deltaTime) { bus.position += Vector3.right * Time.deltaTime * (2 + t * 3); yield return null; }
            yield return Card("On the way to school", "The deadline rides along  ·  Continue  [Space]");
        }
    }
}
