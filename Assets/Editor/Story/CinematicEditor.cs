using System.Collections.Generic;
using System.Linq;
using Mindscape.AcademicPressure;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

/// <summary>One cinematic step in the Inspector: a one-line summary, then only the fields its Type uses, with buttons
/// to make a camera view from the Scene view, look through it, or make a place at the Scene view's centre.</summary>
[CustomPropertyDrawer(typeof(CinematicStep))]
public class CinematicStepDrawer : PropertyDrawer
{
    static readonly float Line = EditorGUIUtility.singleLineHeight, Gap = EditorGUIUtility.standardVerticalSpacing;

    // The fields each type uses: (field, label).
    static (string field, string label)[] Fields(CinematicStep.Type type)
    {
        switch (type)
        {
            case CinematicStep.Type.CameraCut: return new[] { ("target", "View") };
            case CinematicStep.Type.CameraGlide: return new[] { ("target", "View"), ("seconds", "Seconds") };
            case CinematicStep.Type.Line: return new[] { ("speaker", "Speaker"), ("text", "Words") };
            case CinematicStep.Type.Choice: return new[] { ("speaker", "Title"), ("text", "Question"), ("options", "Answers"), ("saveAs", "Save answer as") };
            case CinematicStep.Type.TitleCard: return new[] { ("text", "Words") };
            case CinematicStep.Type.FadeOut: case CinematicStep.Type.FadeIn: case CinematicStep.Type.Wait: return new[] { ("seconds", "Seconds") };
            case CinematicStep.Type.ShowPicture: return new[] { ("picture", "Picture"), ("text", "Caption") };
            case CinematicStep.Type.PlayCutscene: return new[] { ("cutscene", "Cutscene") };
            case CinematicStep.Type.PersonWalk: return new[] { ("person", "Person"), ("target", "Walk to"), ("seconds", "Seconds") };
            case CinematicStep.Type.PersonPlace: return new[] { ("person", "Person"), ("target", "Stand at") };
            case CinematicStep.Type.PersonTurn: return new[] { ("person", "Person"), ("target", "Look at"), ("seconds", "Seconds") };
            case CinematicStep.Type.PersonAnimation: return new[] { ("person", "Person"), ("animation", "Animation") };
            case CinematicStep.Type.PlayerMove: return new[] { ("target", "Move to") };
            case CinematicStep.Type.ShowObject: case CinematicStep.Type.HideObject: return new[] { ("obj", "Object") };
            case CinematicStep.Type.Breathing: return new[] { ("seconds", "Seconds") };
            case CinematicStep.Type.Conversation: return new[] { ("conversation", "Conversation") };
            case CinematicStep.Type.WriteAnswer: return new[] { ("speaker", "Title"), ("text", "Question"), ("saveAs", "Save answer as") };
            case CinematicStep.Type.PhoneOpen: return new[] { ("speaker", "Chat with") };
            case CinematicStep.Type.PhoneMessage: return new[] { ("speaker", "From"), ("text", "Message") };
            case CinematicStep.Type.PhoneReply: return new[] { ("options", "Replies"), ("saveAs", "Save reply as") };
            case CinematicStep.Type.FlashbackStart: return new[] { ("text", "Label"), ("seconds", "Fade seconds") };
            case CinematicStep.Type.FlashbackEnd: return new[] { ("seconds", "Fade seconds") };
            case CinematicStep.Type.Exam: return new[] { ("exam", "Exam paper"), ("saveAs", "Save number answered as") };
            case CinematicStep.Type.WorryCourtroom: return new[] { ("worryCase", "Case"), ("minigame", "Courtroom prefab"), ("saveAs", "Save balanced thought as") };
            case CinematicStep.Type.Practice: return new[] { ("minigame", "Minigame"), ("saveAs", "Save result as") };
            case CinematicStep.Type.Stress: return new[] { ("amount", "Amount (+ raises, - lowers)") };
            default: return new (string, string)[0];
        }
    }

    static bool IsCamera(CinematicStep.Type t) => t == CinematicStep.Type.CameraCut || t == CinematicStep.Type.CameraGlide;
    static bool HasPlace(CinematicStep.Type t) => t == CinematicStep.Type.PersonWalk || t == CinematicStep.Type.PersonPlace || t == CinematicStep.Type.PersonTurn || t == CinematicStep.Type.PlayerMove;

    static string Summary(SerializedProperty p)
    {
        var type = (CinematicStep.Type)p.FindPropertyRelative("type").enumValueIndex;
        string Obj(string f) { var o = p.FindPropertyRelative(f).objectReferenceValue; return o != null ? o.name : "(none)"; }
        string Text(string f, int max = 46) { var s = p.FindPropertyRelative(f).stringValue ?? ""; s = s.Replace("\n", " "); return s.Length > max ? s.Substring(0, max) + "…" : s; }
        float sec = p.FindPropertyRelative("seconds").floatValue;
        switch (type)
        {
            case CinematicStep.Type.CameraCut: return "Camera cut → " + Obj("target");
            case CinematicStep.Type.CameraGlide: return "Camera glide → " + Obj("target") + " (" + sec + " s)";
            case CinematicStep.Type.Line: { string who = p.FindPropertyRelative("speaker").stringValue; return (string.IsNullOrWhiteSpace(who) ? "Narration" : who) + ": " + Text("text"); }
            case CinematicStep.Type.Choice: return "Choice: " + Text("text");
            case CinematicStep.Type.TitleCard: return "Title card: " + Text("text");
            case CinematicStep.Type.FadeOut: return "Fade to black (" + sec + " s)";
            case CinematicStep.Type.FadeIn: return "Fade from black (" + sec + " s)";
            case CinematicStep.Type.ShowPicture: return "Show picture " + Obj("picture");
            case CinematicStep.Type.HidePicture: return "Hide the picture";
            case CinematicStep.Type.PlayCutscene: return "Cutscene " + Obj("cutscene");
            case CinematicStep.Type.PersonWalk: return Obj("person") + " walks to " + Obj("target");
            case CinematicStep.Type.PersonPlace: return Obj("person") + " stands at " + Obj("target");
            case CinematicStep.Type.PersonTurn: return Obj("person") + " looks at " + Obj("target");
            case CinematicStep.Type.PersonAnimation: return Obj("person") + " plays " + p.FindPropertyRelative("animation").stringValue;
            case CinematicStep.Type.PlayerMove: return "Player moves to " + Obj("target");
            case CinematicStep.Type.ShowObject: return "Show " + Obj("obj");
            case CinematicStep.Type.HideObject: return "Hide " + Obj("obj");
            case CinematicStep.Type.Breathing: return "Breathing exercise";
            case CinematicStep.Type.Wait: return "Wait " + sec + " s";
            case CinematicStep.Type.Conversation: return "Conversation " + Obj("conversation");
            case CinematicStep.Type.WriteAnswer: return "Write an answer: " + Text("text");
            case CinematicStep.Type.PhoneOpen: return "Phone: chat with " + p.FindPropertyRelative("speaker").stringValue;
            case CinematicStep.Type.PhoneMessage: return "Phone, " + (string.IsNullOrWhiteSpace(p.FindPropertyRelative("speaker").stringValue) ? "them" : p.FindPropertyRelative("speaker").stringValue) + ": " + Text("text");
            case CinematicStep.Type.PhoneReply: return "Phone: pick a reply (" + p.FindPropertyRelative("options").arraySize + ")";
            case CinematicStep.Type.PhoneClose: return "Phone: close";
            case CinematicStep.Type.FlashbackStart: return "Flashback starts: " + Text("text");
            case CinematicStep.Type.FlashbackEnd: return "Flashback ends";
            case CinematicStep.Type.Exam: return "Minigame: exam " + Obj("exam");
            case CinematicStep.Type.WorryCourtroom: return "Minigame: Worry Courtroom " + Obj("worryCase");
            case CinematicStep.Type.Practice: return "Minigame: " + Obj("minigame");
            case CinematicStep.Type.Stress: { float a = p.FindPropertyRelative("amount").floatValue; return "Stress " + (a >= 0 ? "+" : "") + a; }
        }
        return type.ToString();
    }

    public const string CourtroomPrefab = "Assets/Prefabs/Minigames/WorryCourtroom.prefab";

    // The Worry Courtroom step needs the courtroom prefab: filled in by itself.
    static void AutoFill(SerializedProperty p, CinematicStep.Type type)
    {
        var minigame = p.FindPropertyRelative("minigame");
        if (type == CinematicStep.Type.WorryCourtroom && minigame.objectReferenceValue == null)
            minigame.objectReferenceValue = AssetDatabase.LoadAssetAtPath<GameObject>(CourtroomPrefab);
    }

    // What the step still needs to play (it is skipped without it), or null.
    static string Missing(SerializedProperty p, CinematicStep.Type type)
    {
        bool None(string f) => p.FindPropertyRelative(f).objectReferenceValue == null;
        switch (type)
        {
            case CinematicStep.Type.Conversation: return None("conversation") ? "Drag a Conversation asset here (Mindscape › Story › New Conversation)." : null;
            case CinematicStep.Type.Exam: return None("exam") ? "Drag an Exam Paper asset here (Assets › Create › Mindscape › Exam Paper)." : null;
            case CinematicStep.Type.WorryCourtroom: return None("worryCase") ? "Drag a case here (Assets/Minigames/WorryCourtroom/Cases)." : null;
            case CinematicStep.Type.Practice:
                {
                    var go = p.FindPropertyRelative("minigame").objectReferenceValue as GameObject;
                    if (go == null) return "Drag a minigame prefab here (Assets/Prefabs/Minigames, for example MemoryMatchMinigame).";
                    return go.GetComponent<Mindscape.Minigames.MinigamePopup>() == null ? "That prefab is not a practice minigame. Use one from Assets/Prefabs/Minigames." : null;
                }
            case CinematicStep.Type.PhoneReply: return p.FindPropertyRelative("options").arraySize == 0 ? "Add at least one reply." : null;
        }
        return null;
    }

    public override float GetPropertyHeight(SerializedProperty property, GUIContent label)
    {
        float h = Line + Gap;
        if (!property.isExpanded) return h;
        var type = (CinematicStep.Type)property.FindPropertyRelative("type").enumValueIndex;
        h += Line + Gap;
        foreach (var (f, _) in Fields(type)) h += EditorGUI.GetPropertyHeight(property.FindPropertyRelative(f), true) + Gap;
        if (IsCamera(type) || HasPlace(type)) h += Line + Gap;
        if (Missing(property, type) != null) h += Line * 2 + Gap;
        return h;
    }

    public override void OnGUI(Rect position, SerializedProperty property, GUIContent label)
    {
        EditorGUI.BeginProperty(position, label, property);
        var row = new Rect(position.x, position.y, position.width, Line);
        string index = label.text.Replace("Element ", "");
        int.TryParse(index, out int n);
        property.isExpanded = EditorGUI.Foldout(row, property.isExpanded, (n + 1) + ".  " + Summary(property), true);
        if (property.isExpanded)
        {
            EditorGUI.indentLevel++;
            row.y += Line + Gap;
            var typeProp = property.FindPropertyRelative("type");
            EditorGUI.PropertyField(row, typeProp, new GUIContent("Type"));
            var type = (CinematicStep.Type)typeProp.enumValueIndex;
            row.y += Line + Gap;
            foreach (var (f, l) in Fields(type))
            {
                var p = property.FindPropertyRelative(f);
                float h = EditorGUI.GetPropertyHeight(p, true);
                EditorGUI.PropertyField(new Rect(row.x, row.y, row.width, h), p, new GUIContent(l, p.tooltip), true);
                row.y += h + Gap;
            }
            AutoFill(property, type);
            string missing = Missing(property, type);
            if (missing != null)
            {
                EditorGUI.HelpBox(EditorGUI.IndentedRect(new Rect(row.x, row.y, row.width, Line * 2)), missing, MessageType.Warning);
                row.y += Line * 2 + Gap;
            }
            var owner = property.serializedObject.targetObject as Cinematic;
            var target = property.FindPropertyRelative("target");
            if (owner != null && (IsCamera(type) || HasPlace(type)))
            {
                var buttons = EditorGUI.IndentedRect(row);
                float w = buttons.width / 2 - 2;
                if (IsCamera(type))
                {
                    if (GUI.Button(new Rect(buttons.x, buttons.y, w, Line), new GUIContent("Set view from Scene view", "Makes (or moves) the view object to exactly what the Scene view shows.")))
                        target.objectReferenceValue = CinematicTools.ViewFromSceneView(owner, target.objectReferenceValue as Transform);
                    using (new EditorGUI.DisabledScope(target.objectReferenceValue == null))
                        if (GUI.Button(new Rect(buttons.x + w + 4, buttons.y, w, Line), new GUIContent("Look through it", "Moves the Scene view to this view, to check the shot.")))
                            CinematicTools.LookThrough((Transform)target.objectReferenceValue);
                }
                else
                {
                    if (GUI.Button(new Rect(buttons.x, buttons.y, w, Line), new GUIContent("New place at Scene view centre", "Makes a place object on the floor at the middle of the Scene view.")))
                        target.objectReferenceValue = CinematicTools.PlaceAtSceneView(owner, "Place");
                    using (new EditorGUI.DisabledScope(target.objectReferenceValue == null))
                        if (GUI.Button(new Rect(buttons.x + w + 4, buttons.y, w, Line), "Select it"))
                        { Selection.activeObject = target.objectReferenceValue; SceneView.lastActiveSceneView?.FrameSelected(); }
                }
            }
            EditorGUI.indentLevel--;
        }
        EditorGUI.EndProperty();
    }
}

[CustomEditor(typeof(Cinematic))]
public class CinematicInspector : Editor
{
    public override void OnInspectorGUI()
    {
        serializedObject.Update();
        var c = (Cinematic)target;
        EditorGUILayout.HelpBox("A cinematic plays its steps in order. Pick when it plays, then add steps with the buttons below (or + on the list). Click a step to open it.", MessageType.Info);
        var trigger = serializedObject.FindProperty("trigger");
        EditorGUILayout.PropertyField(trigger, new GUIContent("Plays"));
        var when = (Cinematic.When)trigger.enumValueIndex;
        if (when == Cinematic.When.OnArrival || when == Cinematic.When.OnInteract)
        {
            using (new EditorGUILayout.HorizontalScope())
            {
                EditorGUILayout.PropertyField(serializedObject.FindProperty("place"));
                if (GUILayout.Button(new GUIContent("Here", "Makes the place at the middle of the Scene view."), GUILayout.Width(50)))
                    serializedObject.FindProperty("place").objectReferenceValue = CinematicTools.PlaceAtSceneView(c, "Place");
            }
            if (when == Cinematic.When.OnInteract) EditorGUILayout.PropertyField(serializedObject.FindProperty("prompt"), new GUIContent("[E] prompt"));
            EditorGUILayout.PropertyField(serializedObject.FindProperty("range"));
            if (c.place == null) EditorGUILayout.HelpBox("Set the Place (or click Here): without it this cinematic never plays.", MessageType.Warning);
        }
        else if (when == Cinematic.When.FromScript)
            EditorGUILayout.HelpBox("Plays only from a script: yield return PlayCinematic(cinematic);", MessageType.None);
        EditorGUILayout.PropertyField(serializedObject.FindProperty("onlyOnce"));

        EditorGUILayout.Space(6);
        EditorGUILayout.LabelField("Add a step", EditorStyles.boldLabel);
        using (new EditorGUILayout.HorizontalScope())
        {
            if (GUILayout.Button("Camera view\nfrom Scene view", GUILayout.Height(34))) Add(c, CinematicStep.Type.CameraCut, s => s.target = CinematicTools.ViewFromSceneView(c, null));
            if (GUILayout.Button("Line of\ndialogue", GUILayout.Height(34))) Add(c, CinematicStep.Type.Line, s => { s.speaker = "Mom"; s.text = "Write the words here."; });
            if (GUILayout.Button("Choice", GUILayout.Height(34))) Add(c, CinematicStep.Type.Choice, s => { s.text = "What do you say?"; s.options = new List<string> { "First answer", "Second answer" }; });
            if (GUILayout.Button("Fade\nout + in", GUILayout.Height(34))) { Add(c, CinematicStep.Type.FadeOut, s => s.seconds = .6f); Add(c, CinematicStep.Type.FadeIn, s => s.seconds = .6f); }
            if (GUILayout.Button("Wait", GUILayout.Height(34))) Add(c, CinematicStep.Type.Wait, s => s.seconds = 1);
        }
        using (new EditorGUILayout.HorizontalScope())
        {
            if (GUILayout.Button("Conversation\n(asset)", GUILayout.Height(34))) Add(c, CinematicStep.Type.Conversation, s => s.conversation = ConversationTools.Latest());
            if (GUILayout.Button("Phone\nchat", GUILayout.Height(34)))
            {
                Add(c, CinematicStep.Type.PhoneOpen, s => s.speaker = "Mom");
                Add(c, CinematicStep.Type.PhoneMessage, s => { s.speaker = "Mom"; s.text = "Write the message here."; });
                Add(c, CinematicStep.Type.PhoneReply, s => s.options = new List<string> { "First reply", "Second reply" });
                Add(c, CinematicStep.Type.PhoneClose, s => { });
            }
            if (GUILayout.Button("Exam\npaper", GUILayout.Height(34))) Add(c, CinematicStep.Type.Exam, s => s.exam = ConversationTools.Latest<Mindscape.Minigames.ExamPaper>());
            if (GUILayout.Button("Worry\nCourtroom", GUILayout.Height(34))) Add(c, CinematicStep.Type.WorryCourtroom, s => s.minigame = AssetDatabase.LoadAssetAtPath<GameObject>(CinematicStepDrawer.CourtroomPrefab));
            if (GUILayout.Button("Practice\nminigame", GUILayout.Height(34))) Add(c, CinematicStep.Type.Practice, s => { });
            if (GUILayout.Button("Breathing", GUILayout.Height(34))) Add(c, CinematicStep.Type.Breathing, s => s.seconds = 15);
        }
        EditorGUILayout.Space(4);
        EditorGUILayout.PropertyField(serializedObject.FindProperty("steps"), new GUIContent("Steps (" + c.steps.Count + ")"), true);
        serializedObject.ApplyModifiedProperties();
    }

    void Add(Cinematic c, CinematicStep.Type type, System.Action<CinematicStep> fill)
    {
        serializedObject.ApplyModifiedProperties();
        Undo.RecordObject(c, "Add cinematic step");
        var step = new CinematicStep { type = type };
        fill(step);
        c.steps.Add(step);
        EditorUtility.SetDirty(c);
        serializedObject.Update();
    }
}

/// <summary>Mindscape › Story › New Cinematic, and the helpers behind the Inspector buttons.</summary>
public static class CinematicTools
{
    [MenuItem("Mindscape/Story/New Cinematic (in the open scene)", priority = 2)]
    public static void NewCinematic()
    {
        var episode = Object.FindFirstObjectByType<AcademicEpisode>(FindObjectsInactive.Include);
        var go = new GameObject("Cinematic - New");
        Undo.RegisterCreatedObjectUndo(go, "New cinematic");
        if (episode != null) go.transform.SetParent(episode.transform, false);
        go.transform.position = GroundAt(SceneCentre());
        var c = go.AddComponent<Cinematic>();
        c.trigger = Cinematic.When.OnInteract;
        c.prompt = "Look";
        c.place = PlaceAtSceneView(c, "Place");
        c.steps.Add(new CinematicStep { type = CinematicStep.Type.CameraCut, target = ViewFromSceneView(c, null) });
        c.steps.Add(new CinematicStep { type = CinematicStep.Type.Line, speaker = "", text = "Write the first line here." });
        EditorSceneManager.MarkSceneDirty(go.scene);
        Selection.activeGameObject = go;
        Debug.Log("[New Cinematic] Made '" + go.name + "'" + (episode != null ? " inside " + episode.name : "") + ": a place at the middle of the Scene view, a camera view from the Scene view and one line. Edit it in the Inspector.");
    }

    static Vector3 SceneCentre() => SceneView.lastActiveSceneView != null ? SceneView.lastActiveSceneView.pivot : Vector3.zero;

    static Vector3 GroundAt(Vector3 p)
    {
        Physics.SyncTransforms();
        return Physics.Raycast(p + Vector3.up * 2, Vector3.down, out var hit, 20, ~0, QueryTriggerInteraction.Ignore) ? hit.point : p;
    }

    static Transform Child(Cinematic owner, string baseName)
    {
        int n = 1;
        while (owner.transform.Find(baseName + " " + n) != null) n++;
        var t = new GameObject(baseName + " " + n).transform;
        Undo.RegisterCreatedObjectUndo(t.gameObject, "Add " + baseName);
        t.SetParent(owner.transform, false);
        return t;
    }

    /// <summary>A view object (made under the cinematic if needed) set to exactly what the Scene view shows.</summary>
    public static Transform ViewFromSceneView(Cinematic owner, Transform view)
    {
        if (view == null) view = Child(owner, "View");
        var sv = SceneView.lastActiveSceneView;
        if (sv != null)
        {
            Undo.RecordObject(view, "Set view");
            view.SetPositionAndRotation(sv.camera.transform.position, sv.camera.transform.rotation);
        }
        EditorSceneManager.MarkSceneDirty(owner.gameObject.scene);
        return view;
    }

    /// <summary>A place object on the floor at the middle of the Scene view, facing away from the Scene view camera.</summary>
    public static Transform PlaceAtSceneView(Cinematic owner, string baseName)
    {
        var place = Child(owner, baseName);
        var sv = SceneView.lastActiveSceneView;
        place.position = GroundAt(SceneCentre());
        if (sv != null)
        {
            var look = Vector3.ProjectOnPlane(sv.camera.transform.forward, Vector3.up);
            if (look.sqrMagnitude > .01f) place.rotation = Quaternion.LookRotation(-look);
        }
        EditorSceneManager.MarkSceneDirty(owner.gameObject.scene);
        return place;
    }

    /// <summary>Moves the Scene view to look through a view object.</summary>
    public static void LookThrough(Transform view)
    {
        var sv = SceneView.lastActiveSceneView;
        if (sv == null || view == null) return;
        sv.AlignViewToObject(view);
        sv.Repaint();
    }
}
