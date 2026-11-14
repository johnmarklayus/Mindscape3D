using System.Collections;
using Mindscape.Data;
using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.UI;

namespace Mindscape.Cutscenes
{
    /// <summary>
    /// Plays a CutsceneAsset on top of whatever is on screen: each slide's picture fills the screen, its words sit in a
    /// dark plate at the bottom, and the player moves on with Space / Enter / E / click / tap / gamepad A (or it moves on
    /// by itself after the slide's seconds). Esc skips the rest when the cutscene allows it. Built at runtime, so it
    /// works in any scene, with or without an episode.
    /// </summary>
    public static class CutscenePlayback
    {
        public static bool IsPlaying { get; private set; }

        public static IEnumerator Play(CutsceneAsset cutscene)
        {
            if (cutscene == null || cutscene.slides.Count == 0) yield break;
            IsPlaying = true;
            var ui = Build();
            AudioSource source = null;
            if (cutscene.music != null)
            {
                MusicManager.SetPaused(true);
                source = ui.root.AddComponent<AudioSource>();
                source.clip = cutscene.music; source.loop = true; source.volume = cutscene.musicVolume; source.Play();
            }
            ui.hint.text = cutscene.canSkip ? "Space  Next        Esc  Skip" : "Space  Next";
            bool skipped = false;
            for (int i = 0; i < cutscene.slides.Count && !skipped; i++)
            {
                var slide = cutscene.slides[i];
                ui.image.texture = slide.image;
                ui.image.color = slide.image != null ? Color.white : Color.black;
                if (slide.image != null) ui.fitter.aspectRatio = (float)slide.image.width / Mathf.Max(1, slide.image.height);
                ui.speaker.text = MindscapeDatabase.Personalize(slide.speaker ?? "");
                ui.text.text = MindscapeDatabase.Personalize(slide.text ?? "");
                bool hasWords = !string.IsNullOrWhiteSpace(slide.text) || !string.IsNullOrWhiteSpace(slide.speaker);
                ui.plate.SetActive(hasWords);
                ui.speaker.gameObject.SetActive(!string.IsNullOrWhiteSpace(slide.speaker));
                yield return Fade(ui.slide, 0, 1, cutscene.fadeSeconds);

                float shown = 0;
                while (true)
                {
                    shown += Time.unscaledDeltaTime;
                    if (cutscene.canSkip && SkipPressed()) { skipped = true; break; }
                    if (shown > .25f && NextPressed()) break;
                    if (slide.autoAdvanceSeconds > 0 && shown >= slide.autoAdvanceSeconds) break;
                    yield return null;
                }
                yield return Fade(ui.slide, 1, 0, cutscene.fadeSeconds);
            }
            if (source != null) { source.Stop(); MusicManager.SetPaused(false); }
            Object.Destroy(ui.root);
            IsPlaying = false;
        }

        static IEnumerator Fade(CanvasGroup group, float from, float to, float seconds)
        {
            for (float t = 0; t < seconds; t += Time.unscaledDeltaTime) { group.alpha = Mathf.Lerp(from, to, t / seconds); yield return null; }
            group.alpha = to;
        }

        static bool NextPressed()
        {
            var k = Keyboard.current;
            if (k != null && (k.spaceKey.wasPressedThisFrame || k.enterKey.wasPressedThisFrame || k.numpadEnterKey.wasPressedThisFrame || k.eKey.wasPressedThisFrame || k.rightArrowKey.wasPressedThisFrame)) return true;
            if (Mouse.current != null && Mouse.current.leftButton.wasPressedThisFrame) return true;
            if (Touchscreen.current != null && Touchscreen.current.primaryTouch.press.wasPressedThisFrame) return true;
            return Gamepad.current != null && Gamepad.current.buttonSouth.wasPressedThisFrame;
        }

        static bool SkipPressed() =>
            (Keyboard.current != null && Keyboard.current.escapeKey.wasPressedThisFrame) ||
            (Gamepad.current != null && Gamepad.current.startButton.wasPressedThisFrame);

        // ---------------------------------------------------------------- the overlay

        struct Overlay
        {
            public GameObject root, plate;
            public CanvasGroup slide;
            public RawImage image;
            public AspectRatioFitter fitter;
            public Text speaker, text, hint;
        }

        static Overlay Build()
        {
            var o = new Overlay();
            o.root = new GameObject("Cutscene");
            var canvas = o.root.AddComponent<Canvas>();
            canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            canvas.sortingOrder = 30000;   // over the story screens, under the loading screen
            var scaler = o.root.AddComponent<CanvasScaler>();
            scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
            scaler.referenceResolution = new Vector2(1920, 1080);
            scaler.matchWidthOrHeight = .5f;

            var black = Rect("Black", o.root.transform); Stretch(black);
            black.gameObject.AddComponent<Image>().color = Color.black;

            var slide = Rect("Slide", o.root.transform); Stretch(slide);
            o.slide = slide.gameObject.AddComponent<CanvasGroup>(); o.slide.alpha = 0;
            var frame = Rect("Picture Frame", slide); Stretch(frame);
            frame.gameObject.AddComponent<RectMask2D>();
            var picture = Rect("Picture", frame);
            picture.anchorMin = picture.anchorMax = new Vector2(.5f, .5f);
            o.image = picture.gameObject.AddComponent<RawImage>();
            o.fitter = picture.gameObject.AddComponent<AspectRatioFitter>();
            o.fitter.aspectMode = AspectRatioFitter.AspectMode.EnvelopeParent;
            o.fitter.aspectRatio = 16f / 9f;

            var plate = Rect("Words", slide);
            plate.anchorMin = new Vector2(.08f, .06f); plate.anchorMax = new Vector2(.92f, .3f);
            plate.offsetMin = plate.offsetMax = Vector2.zero;
            plate.gameObject.AddComponent<Image>().color = new Color(.09f, .07f, .05f, .84f);
            o.plate = plate.gameObject;

            var serif = Resources.Load<Font>("MainMenuNew/StorySerif");
            var body = Resources.Load<Font>("MinigameTheme/ComicNeue-Regular");
            var fallback = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            o.speaker = Label("Speaker", plate, serif ? serif : fallback, 34, new Color(.94f, .74f, .38f), TextAnchor.UpperLeft);
            Anchor(o.speaker.rectTransform, new Vector2(0, .72f), new Vector2(1, 1), new Vector2(36, 0), new Vector2(-36, -14));
            o.text = Label("Text", plate, body ? body : fallback, 34, new Color(.94f, .89f, .8f), TextAnchor.MiddleCenter);
            Anchor(o.text.rectTransform, Vector2.zero, new Vector2(1, .8f), new Vector2(40, 14), new Vector2(-40, 0));
            o.hint = Label("Hint", o.root.transform, body ? body : fallback, 22, new Color(1, 1, 1, .55f), TextAnchor.LowerRight);
            Anchor(o.hint.rectTransform, new Vector2(.5f, 0), new Vector2(1, .05f), Vector2.zero, new Vector2(-40, 0));
            return o;
        }

        static RectTransform Rect(string name, Transform parent)
        {
            var go = new GameObject(name, typeof(RectTransform));
            go.transform.SetParent(parent, false);
            return (RectTransform)go.transform;
        }

        static void Stretch(RectTransform r) { r.anchorMin = Vector2.zero; r.anchorMax = Vector2.one; r.offsetMin = r.offsetMax = Vector2.zero; }

        static void Anchor(RectTransform r, Vector2 min, Vector2 max, Vector2 offsetMin, Vector2 offsetMax)
        {
            r.anchorMin = min; r.anchorMax = max; r.offsetMin = offsetMin; r.offsetMax = offsetMax;
        }

        static Text Label(string name, Transform parent, Font font, int size, Color color, TextAnchor anchor)
        {
            var t = Rect(name, parent).gameObject.AddComponent<Text>();
            t.font = font; t.fontSize = size; t.color = color; t.alignment = anchor;
            t.horizontalOverflow = HorizontalWrapMode.Wrap; t.verticalOverflow = VerticalWrapMode.Overflow;
            t.raycastTarget = false;
            return t;
        }
    }
}
