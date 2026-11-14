using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using Mindscape.Cutscenes;
using Mindscape.Data;
using UnityEngine;

namespace Mindscape.AcademicPressure
{
    // Cinematics and cutscenes made in the Inspector (Cinematic.cs, CutsceneAsset.cs), in every episode:
    //   * the chapter asset's "Cutscene Before" for this episode plays first (Chapter 4 and later);
    //   * Cinematics set to "At the start of the episode" play next, in Hierarchy order;
    //   * Cinematics set to play at a place become spots (walk there, or press E there) for the whole episode;
    //   * then the episode's own story (Play) starts.
    // A script can also play one: yield return PlayCinematic(cinematic); or yield return PlayCutscene(cutscene);
    public abstract partial class AcademicEpisode
    {
        IEnumerator PlayWithCinematics()
        {
            // Hierarchy order, so the spots keep the same order every time (loading a save replays spots by order).
            var cinematics = FindObjectsByType<Cinematic>(FindObjectsInactive.Exclude, FindObjectsSortMode.None)
                .OrderBy(c => HierarchyPath(c.transform), StringComparer.Ordinal).ToList();
            foreach (var c in cinematics)
            {
                if (c.place == null || (c.trigger != Cinematic.When.OnArrival && c.trigger != Cinematic.When.OnInteract)) continue;
                var cinematic = c;
                Func<bool> open = () => !(cinematic.onlyOnce && cinematic.played);
                if (c.trigger == Cinematic.When.OnArrival) AddArrival(c.place, c.prompt, open, () => PlayCinematic(cinematic), c.range);
                else AddSpot(c.place, c.prompt, open, () => PlayCinematic(cinematic), c.range);
            }
            if (!Replaying)
            {
                var before = StoryChapters.Episode(Chapter, Episode)?.cutsceneBefore;
                if (before != null) yield return PlayCutscene(before);
                foreach (var c in cinematics.Where(c => c.trigger == Cinematic.When.AtStart)) yield return PlayCinematic(c);
            }
            yield return Play();
        }

        static string HierarchyPath(Transform t) => t.parent == null ? t.GetSiblingIndex().ToString("0000") : HierarchyPath(t.parent) + "/" + t.GetSiblingIndex().ToString("0000");

        /// <summary>
        /// Lets the player walk freely until every cinematic set to play at a place (once) has played. A cinematic at a
        /// place can only start while the player is walking; with none in the scene this returns at once.
        /// </summary>
        protected IEnumerator RoamUntilCinematicsDone(string objective = "Look around")
        {
            var waiting = FindObjectsByType<Cinematic>(FindObjectsInactive.Exclude, FindObjectsSortMode.None)
                .Where(c => c.place != null && c.onlyOnce && !c.played && (c.trigger == Cinematic.When.OnArrival || c.trigger == Cinematic.When.OnInteract))
                .OrderBy(c => HierarchyPath(c.transform), StringComparer.Ordinal).ToList();
            if (waiting.Count == 0) yield break;
            SetObjective(objective, string.Concat(waiting.Select(c => Check(false, c.trigger == Cinematic.When.OnInteract ? c.prompt : c.name.Replace("Cinematic - ", "")))));
            yield return RoamUntil(() => waiting.All(c => c.played));
        }

        /// <summary>Plays a slide cutscene over the episode.</summary>
        protected IEnumerator PlayCutscene(CutsceneAsset cutscene)
        {
            if (cutscene == null) yield break;
            SetLocked(true);
            yield return CutscenePlayback.Play(cutscene);
        }

        /// <summary>Plays a cinematic's steps in order. Consecutive lines of dialogue share one "x / n" counter.</summary>
        public IEnumerator PlayCinematic(Cinematic cinematic)
        {
            if (cinematic == null) yield break;
            cinematic.played = true;
            SetLocked(true);
            var steps = cinematic.steps;
            for (int i = 0; i < steps.Count; i++)
            {
                var step = steps[i];
                if (step.type == CinematicStep.Type.Line)
                {
                    // This line and the ones right after it, as one dialogue.
                    var lines = new List<IEnumerator>();
                    while (i < steps.Count && steps[i].type == CinematicStep.Type.Line) lines.Add(Line(steps[i++]));
                    i--;
                    yield return DialogueSequence(lines.ToArray());
                    continue;
                }
                yield return Step(step);
            }
        }

        IEnumerator Line(CinematicStep s) => Spoken(s.speaker, s.text);

        IEnumerator Step(CinematicStep s)
        {
            switch (s.type)
            {
                case CinematicStep.Type.CameraCut:
                    if (s.target != null) ShotFromView(s.target);
                    break;
                case CinematicStep.Type.CameraGlide:
                    if (s.target != null) yield return Glide(s.target.position, s.target.position + s.target.forward * 4, Mathf.Max(.05f, s.seconds));
                    break;
                case CinematicStep.Type.Choice:
                    if (s.options.Count == 0) break;
                    int picked = 0;
                    yield return Choose(string.IsNullOrWhiteSpace(s.speaker) ? "Your answer" : s.speaker, MindscapeDatabase.Personalize(s.text ?? ""), s.options, i => picked = i);
                    if (!string.IsNullOrWhiteSpace(s.saveAs)) Record(s.saveAs.Trim(), s.options[picked]);
                    break;
                case CinematicStep.Type.TitleCard:
                    yield return Card(MindscapeDatabase.Personalize(s.text ?? ""));
                    break;
                case CinematicStep.Type.FadeOut:
                    yield return Fade(0, 1, Mathf.Max(.05f, s.seconds));
                    break;
                case CinematicStep.Type.FadeIn:
                    yield return Fade(1, 0, Mathf.Max(.05f, s.seconds));
                    break;
                case CinematicStep.Type.ShowPicture:
                    ShowPhoto(s.picture, MindscapeDatabase.Personalize(s.text ?? ""));
                    break;
                case CinematicStep.Type.HidePicture:
                    HidePhoto();
                    break;
                case CinematicStep.Type.PlayCutscene:
                    yield return PlayCutscene(s.cutscene);
                    SetLocked(true);
                    break;
                case CinematicStep.Type.PersonWalk:
                    if (s.person != null && s.target != null)
                    {
                        yield return HomeWelcome.StepToward(s.person, s.target.position, Mathf.Max(.1f, s.seconds));
                        yield return HomeWelcome.TurnTo(s.person, s.person.position + s.target.forward, .25f);
                    }
                    break;
                case CinematicStep.Type.PersonPlace:
                    if (s.person != null && s.target != null) HomeWelcome.Place(s.person, s.target.position, s.target.position + s.target.forward);
                    break;
                case CinematicStep.Type.PersonTurn:
                    if (s.person != null && s.target != null) yield return HomeWelcome.TurnTo(s.person, s.target.position, Mathf.Max(.05f, s.seconds));
                    break;
                case CinematicStep.Type.PersonAnimation:
                    if (s.person != null && !string.IsNullOrWhiteSpace(s.animation)) HomeWelcome.Play(s.person, s.animation.Trim());
                    break;
                case CinematicStep.Type.PlayerMove:
                    if (s.target != null) Teleport(s.target.position, s.target.eulerAngles.y);
                    break;
                case CinematicStep.Type.ShowObject:
                    if (s.obj != null) s.obj.SetActive(true);
                    break;
                case CinematicStep.Type.HideObject:
                    if (s.obj != null) s.obj.SetActive(false);
                    break;
                case CinematicStep.Type.Breathing:
                    yield return Breathe(_ => { }, s.seconds > 1 ? s.seconds : 15);
                    break;
                case CinematicStep.Type.Wait:
                    yield return new WaitForSeconds(s.seconds);
                    break;
                case CinematicStep.Type.Conversation:
                    yield return Talk(s.conversation);
                    break;
                case CinematicStep.Type.WriteAnswer:
                    {
                        string written = "";
                        yield return Ask(string.IsNullOrWhiteSpace(s.speaker) ? "Journal" : s.speaker, MindscapeDatabase.Personalize(s.text ?? ""),
                            "Write here…", "", true, 600, "Continue", t => written = t ?? "", allowEmpty: true);
                        if (!string.IsNullOrWhiteSpace(s.saveAs)) Record(s.saveAs.Trim(), written);
                    }
                    break;
                case CinematicStep.Type.PhoneOpen:
                    OpenPhone(string.IsNullOrWhiteSpace(s.speaker) ? "Message" : MindscapeDatabase.Personalize(s.speaker.Trim()));
                    break;
                case CinematicStep.Type.PhoneMessage:
                    {
                        string from = (s.speaker ?? "").Trim().ToLowerInvariant();
                        bool mine = from == "joey" || from == "me" || from == "player" || s.speaker == PlayerName;
                        yield return PhoneMessage(mine, MindscapeDatabase.Personalize(s.text ?? ""));
                    }
                    break;
                case CinematicStep.Type.PhoneReply:
                    if (s.options.Count == 0) break;
                    {
                        int reply = 0;
                        yield return PhoneChoose(s.options, i => reply = i);
                        if (!string.IsNullOrWhiteSpace(s.saveAs)) Record(s.saveAs.Trim(), s.options[reply]);
                        yield return PhoneMessage(true, MindscapeDatabase.Personalize(s.options[reply]));
                    }
                    break;
                case CinematicStep.Type.PhoneClose:
                    ClosePhone();
                    break;
                case CinematicStep.Type.FlashbackStart:
                    yield return FlashbackIn(string.IsNullOrWhiteSpace(s.text) ? "A memory" : MindscapeDatabase.Personalize(s.text.Trim()), null, Mathf.Max(.05f, s.seconds));
                    break;
                case CinematicStep.Type.FlashbackEnd:
                    yield return FlashbackOut(null, Mathf.Max(.05f, s.seconds));
                    break;
                case CinematicStep.Type.Exam:
                    {
                        var result = new ExamResult();
                        yield return TakeExam(s.exam, r => result = r);
                        if (!string.IsNullOrWhiteSpace(s.saveAs)) Record(s.saveAs.Trim(), result.answered.ToString());
                    }
                    break;
                case CinematicStep.Type.WorryCourtroom:
                    {
                        string reached = "";
                        yield return WorryCourtroom(s.minigame, s.worryCase, (thought, _) => reached = thought);
                        if (!string.IsNullOrWhiteSpace(s.saveAs) && reached.Length > 0) Record(s.saveAs.Trim(), reached);
                    }
                    break;
                case CinematicStep.Type.Practice:
                    {
                        bool done = false;
                        yield return Practice(s.minigame, d => done = d);
                        if (!string.IsNullOrWhiteSpace(s.saveAs)) Record(s.saveAs.Trim(), done ? "completed" : "closed");
                    }
                    break;
                case CinematicStep.Type.Stress:
                    AddStress(s.amount);
                    break;
            }
        }

        /// <summary>The story camera exactly at a view object (its position, looking along its blue arrow).</summary>
        protected void ShotFromView(Transform view)
        {
            UseShotNearClip();
            storyCamera.transform.SetPositionAndRotation(view.position, view.rotation);
            ShotFocus.Set(view.position + view.forward * 4);
        }
    }
}
