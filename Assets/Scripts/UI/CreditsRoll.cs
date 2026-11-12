using System;
using System.Collections;
using TMPro;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.InputSystem;
using UnityEngine.UI;

// The closing credits, nine screens one after another: each fades in, holds, and fades out. Space, Enter, a click or a
// tap moves on to the next screen; Skip (or Esc) ends them. Built from code over whatever scene is open, so the end
// of the story (Chapter 3 Episode 8) and the main menu's About page can both play them.
public sealed class CreditsRoll : MonoBehaviour
{
    // (heading, body) per screen. Headings are the small gold line above the body.
    static readonly (string heading, string body)[] Screens =
    {
        ("", "Thank you for playing MindScape 3D.\nWe hope this journey provided meaningful insights into mindfulness and mental well-being."),
        ("", "MindScape 3D\n<size=60%>A Cross-Platform Online Interactive Simulation Game for Emotional Awareness and Coping Skill Development for Young Adults</size>"),
        ("DEVELOPED BY",
            "<size=60%>PROJECT MANAGER</size>\nJohn Mark V. Layus\n" +
            "<size=60%>LEAD DEVELOPER / PROGRAMMER</size>\nKenn O. Occeño\n" +
            "<size=60%>LEAD 3D ARTIST & ENVIRONMENT DESIGNER</size>\nMark Jason B. Dela Cruz\nMichael Bryan M. Amelanto\n" +
            "<size=60%>UI & GRAPHIC DESIGNER</size>\nAll Team Members\n" +
            "<size=60%>NARRATIVE DESIGNER & QA TESTER</size>\nAll Team Members"),
        ("CAPSTONE ADVISER", "Prince Aron E. Chavez"),
        ("INSTITUTION", "STI College Global City"),
        ("BUILT WITH",
            "<size=60%>DEVELOPMENT HARDWARE</size>\nASUS TUF Gaming A16 Laptop / MSI Katana 15\n" +
            "<size=60%>GAME ENGINE</size>\nUnity Engine\n" +
            "<size=60%>CODE EDITOR</size>\nVisual Studio Code\n" +
            "<size=60%>3D MODELING & ASSETS</size>\nBlender\n" +
            "<size=60%>AUDIO PRODUCTION</size>\nAudacity\n" +
            "<size=60%>DATABASE BACKEND</size>\nSupabase"),
        ("ASSETS AND ATTRIBUTIONS",
            "<size=60%>3D ENVIRONMENT & CHARACTER MODELS</size>\n" +
            "<size=75%>Low-Poly Suburban Houses, Roads, and Street Asset From Scratch\nClassroom Furniture and Interior Props From Scratch\n" +
            "Home Interior Furniture, Bedside Tables, and Household Objects From Scratch\nCustom Low-Poly Human Characters and Chibi-Style Avatars</size>\n" +
            "<size=60%>USER INTERFACE & GRAPHICS</size>\n" +
            "<size=75%>Custom Main Menu Background Illustration and Character Art\nMindScape 3D Tree Logo and Graphic Design\n" +
            "Geometric UI Buttons, Dialogue Windows, and Status Bars</size>"),
        ("SPECIAL THANKS", "To our families, friends, and the faculty of STI College Global City for their unwavering guidance, patience, and support throughout the development of this capstone project."),
        ("DISCLAIMER AND SUPPORT",
            "<size=75%>MindScape 3D is an educational and interactive experience designed for mental health awareness. " +
            "It does not substitute for professional medical advice, diagnosis, or treatment.</size>\n\n" +
            "If you or someone you know is struggling, please reach out to local mental health professionals or trusted support hotlines.\nYou are not alone."),
    };

    static readonly Color Ink = new Color32(18, 24, 27, 255), Gold = new Color32(219, 179, 111, 255), Paper = new Color32(242, 232, 209, 255);

    public static bool IsPlaying { get; private set; }

    /// <summary>Plays the credits over the current scene; 'done' runs after the last screen (or Skip).</summary>
    public static CreditsRoll Play(Action done = null)
    {
        var go = new GameObject("Credits");
        var roll = go.AddComponent<CreditsRoll>();
        roll.done = done;
        return roll;
    }

    Action done;
    CanvasGroup screenGroup;
    TextMeshProUGUI heading, body, hint;
    bool next, skip;
    float shownAt;

    void Awake()
    {
        IsPlaying = true;
        var canvas = gameObject.AddComponent<Canvas>(); canvas.renderMode = RenderMode.ScreenSpaceOverlay; canvas.sortingOrder = 32000;
        var scaler = gameObject.AddComponent<CanvasScaler>(); scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
        scaler.referenceResolution = new Vector2(1920, 1080); scaler.matchWidthOrHeight = .5f;
        gameObject.AddComponent<GraphicRaycaster>();
        if (EventSystem.current == null) new GameObject("EventSystem", typeof(EventSystem), typeof(UnityEngine.InputSystem.UI.InputSystemUIInputModule));

        var back = Rect("Backdrop", transform, Vector2.zero, Vector2.one).gameObject.AddComponent<Image>();
        back.color = Ink;
        // A tap anywhere moves on.
        var tap = back.gameObject.AddComponent<Button>(); tap.transition = Selectable.Transition.None; tap.onClick.AddListener(() => next = true);

        var screen = Rect("Screen", transform, new Vector2(.14f, .1f), new Vector2(.86f, .9f));
        screenGroup = screen.gameObject.AddComponent<CanvasGroup>(); screenGroup.alpha = 0; screenGroup.blocksRaycasts = false;
        heading = Text("Heading", screen, new Vector2(0, .78f), new Vector2(1, .9f), 30, Gold, Font(false));
        heading.characterSpacing = 8;
        body = Text("Body", screen, new Vector2(0, .05f), new Vector2(1, .78f), 46, Paper, Serif());
        body.lineSpacing = 12;

        hint = Text("Hint", transform, new Vector2(.05f, .03f), new Vector2(.6f, .08f), 22, new Color(Paper.r, Paper.g, Paper.b, .55f), Font(false));
        hint.alignment = TextAlignmentOptions.BottomLeft;
        hint.text = Application.isMobilePlatform ? "Tap to continue" : "Space or click to continue";

        var skipButton = Rect("Skip", transform, new Vector2(.86f, .03f), new Vector2(.97f, .09f));
        skipButton.gameObject.AddComponent<Image>().color = new Color32(64, 52, 38, 235);
        var skipLabel = Text("Label", skipButton, Vector2.zero, Vector2.one, 24, Paper, Font(true)); skipLabel.text = "Skip  ›";
        skipButton.gameObject.AddComponent<Button>().onClick.AddListener(() => skip = true);
    }

    IEnumerator Start()
    {
        for (int i = 0; i < Screens.Length && !skip; i++)
        {
            heading.text = Screens[i].heading;
            body.text = Screens[i].body;
            next = false;
            yield return FadeTo(1, .8f);
            shownAt = Time.unscaledTime;
            // Long enough to read: a little more for the longer screens.
            float hold = Mathf.Clamp(4f + body.text.Length / 45f, 5f, 12f);
            while (!next && !skip && Time.unscaledTime - shownAt < hold) yield return null;
            yield return FadeTo(0, .6f);
        }
        IsPlaying = false;
        var then = done;
        Destroy(gameObject);
        then?.Invoke();
    }

    void Update()
    {
        var k = Keyboard.current;
        if (k == null) return;
        if (k.escapeKey.wasPressedThisFrame) skip = true;
        if ((k.spaceKey.wasPressedThisFrame || k.enterKey.wasPressedThisFrame) && Time.unscaledTime - shownAt > .3f) next = true;
    }

    void OnDestroy() => IsPlaying = false;

    IEnumerator FadeTo(float to, float seconds)
    {
        float from = screenGroup.alpha;
        for (float t = 0; t < seconds && !skip; t += Time.unscaledDeltaTime) { screenGroup.alpha = Mathf.Lerp(from, to, t / seconds); yield return null; }
        screenGroup.alpha = to;
    }

    static RectTransform Rect(string name, Transform parent, Vector2 min, Vector2 max)
    {
        var r = new GameObject(name, typeof(RectTransform)).GetComponent<RectTransform>();
        r.SetParent(parent, false); r.anchorMin = min; r.anchorMax = max; r.offsetMin = r.offsetMax = Vector2.zero;
        return r;
    }

    static TextMeshProUGUI Text(string name, Transform parent, Vector2 min, Vector2 max, float size, Color color, TMP_FontAsset font)
    {
        var t = Rect(name, parent, min, max).gameObject.AddComponent<TextMeshProUGUI>();
        if (font != null) t.font = font;
        t.fontSize = size; t.color = color; t.alignment = TextAlignmentOptions.Center; t.textWrappingMode = TextWrappingModes.Normal;
        t.raycastTarget = false;
        return t;
    }

    static TMP_FontAsset Font(bool bold) => Resources.Load<TMP_FontAsset>("MinigameTheme/ComicNeue-" + (bold ? "Bold" : "Regular") + " SDF");
    static TMP_FontAsset Serif() => Resources.Load<TMP_FontAsset>("MinigameTheme/StorySerif SDF") ?? Font(false);
}
