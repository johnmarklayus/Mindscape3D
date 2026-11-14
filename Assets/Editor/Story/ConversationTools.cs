using System.IO;
using Mindscape.AcademicPressure;
using Mindscape.Minigames;
using UnityEditor;
using UnityEngine;

/// <summary>Mindscape › Story › New Conversation / New Exam Paper, and the Inspector rows for their lines.</summary>
public static class ConversationTools
{
    const string ConversationFolder = "Assets/Story/Conversations", ExamFolder = "Assets/Story/Exams";

    [MenuItem("Mindscape/Story/New Conversation", priority = 4)]
    public static void NewConversation()
    {
        var c = ScriptableObject.CreateInstance<Conversation>();
        c.lines.Add(new Conversation.Line { speaker = "Mom", words = "You're home! How was your day?" });
        c.lines.Add(new Conversation.Line { speaker = "Joey", words = "It was okay." });
        c.lines.Add(new Conversation.Line { speaker = "Thought", words = "It feels good to be home." });
        Save(c, ConversationFolder, "Conversation");
    }

    [MenuItem("Mindscape/Story/New Exam Paper", priority = 5)]
    public static void NewExam()
    {
        var e = ScriptableObject.CreateInstance<ExamPaper>();
        e.questions.Add(new ExamPaper.Question { question = "A notebook costs 24 pesos. How much do three notebooks cost?", answers = new System.Collections.Generic.List<string> { "48 pesos", "72 pesos", "96 pesos" } });
        e.questions.Add(new ExamPaper.Question { question = "Write the second question here.", answers = new System.Collections.Generic.List<string> { "First answer", "Second answer", "Third answer" } });
        Save(e, ExamFolder, "Exam Paper");
    }

    static void Save(ScriptableObject asset, string folder, string baseName)
    {
        Directory.CreateDirectory(folder);
        string path = AssetDatabase.GenerateUniqueAssetPath(folder + "/" + baseName + ".asset");
        AssetDatabase.CreateAsset(asset, path);
        AssetDatabase.SaveAssets();
        Selection.activeObject = asset;
        EditorGUIUtility.PingObject(asset);
        Debug.Log("[Mindscape] Made " + path + ". Rename it (F2), then edit it in the Inspector.");
    }

    /// <summary>The asset of that type selected in the Project window, if any (used by the cinematic's step buttons).</summary>
    public static T Latest<T>() where T : Object
    {
        foreach (var o in Selection.objects) if (o is T t) return t;
        return null;
    }

    public static Conversation Latest() => Latest<Conversation>();
}

/// <summary>One line of a conversation on one row: who speaks, then the words.</summary>
[CustomPropertyDrawer(typeof(Conversation.Line))]
public class ConversationLineDrawer : PropertyDrawer
{
    const float SpeakerWidth = 110;

    public override float GetPropertyHeight(SerializedProperty property, GUIContent label)
    {
        var words = property.FindPropertyRelative("words").stringValue ?? "";
        int lines = Mathf.Clamp(words.Split('\n').Length + words.Length / 70, 2, 8);
        return EditorGUIUtility.singleLineHeight * lines + 4;
    }

    public override void OnGUI(Rect position, SerializedProperty property, GUIContent label)
    {
        EditorGUI.BeginProperty(position, label, property);
        var speaker = property.FindPropertyRelative("speaker");
        var words = property.FindPropertyRelative("words");
        var left = new Rect(position.x, position.y + 1, SpeakerWidth, EditorGUIUtility.singleLineHeight);
        speaker.stringValue = EditorGUI.TextField(left, speaker.stringValue);
        var hint = new Rect(left.x, left.yMax + 1, SpeakerWidth, EditorGUIUtility.singleLineHeight);
        string who = string.IsNullOrWhiteSpace(speaker.stringValue) ? "narration" : speaker.stringValue.Trim().ToLowerInvariant() == "thought" ? "the player thinks" :
            speaker.stringValue.Trim().ToLowerInvariant() == "joey" ? "the player says" : "speaks";
        EditorGUI.LabelField(hint, who, EditorStyles.miniLabel);
        var right = new Rect(position.x + SpeakerWidth + 6, position.y + 1, position.width - SpeakerWidth - 6, position.height - 4);
        words.stringValue = EditorGUI.TextArea(right, words.stringValue, new GUIStyle(EditorStyles.textArea) { wordWrap = true });
        EditorGUI.EndProperty();
    }
}

[CustomEditor(typeof(Conversation))]
public class ConversationInspector : Editor
{
    public override void OnInspectorGUI()
    {
        serializedObject.Update();
        EditorGUILayout.HelpBox("Each line: who speaks on the left (a name, Joey for the player, Thought for the player's thoughts, empty for narration), the words on the right. Press Enter in the words for a new line.\n\nPlay it from a cinematic (step \"Dialogue: a conversation\") or a script: yield return Talk(conversation);", MessageType.Info);
        EditorGUILayout.PropertyField(serializedObject.FindProperty("lines"), new GUIContent("Lines (" + ((Conversation)target).lines.Count + ")"), true);
        using (new EditorGUILayout.HorizontalScope())
        {
            var lines = serializedObject.FindProperty("lines");
            void Add(string who) { lines.arraySize++; var l = lines.GetArrayElementAtIndex(lines.arraySize - 1); l.FindPropertyRelative("speaker").stringValue = who; l.FindPropertyRelative("words").stringValue = ""; }
            if (GUILayout.Button("+ Someone speaks")) Add("Mom");
            if (GUILayout.Button("+ Joey speaks")) Add("Joey");
            if (GUILayout.Button("+ A thought")) Add("Thought");
            if (GUILayout.Button("+ Narration")) Add("");
        }
        serializedObject.ApplyModifiedProperties();
    }
}

[CustomEditor(typeof(ExamPaper))]
public class ExamPaperInspector : Editor
{
    public override void OnInspectorGUI()
    {
        serializedObject.Update();
        var paper = (ExamPaper)target;
        EditorGUILayout.HelpBox("Up to " + ExamPaper.MaxQuestions + " questions with up to " + ExamPaper.MaxAnswers + " answers each. No score is shown: the number answered can be saved by the step. Play it from a cinematic (step \"Minigame: exam paper\").", MessageType.Info);
        EditorGUILayout.PropertyField(serializedObject.FindProperty("seconds"), new GUIContent("Seconds on the clock"));
        EditorGUILayout.PropertyField(serializedObject.FindProperty("grounding"), new GUIContent("Grounding break"));
        EditorGUILayout.PropertyField(serializedObject.FindProperty("worry"), new GUIContent("Worried thought"));
        if (paper.grounding) EditorGUILayout.PropertyField(serializedObject.FindProperty("calm"), new GUIContent("Calm thought (after the break)"));
        EditorGUILayout.PropertyField(serializedObject.FindProperty("questions"), true);
        if (paper.questions.Count > ExamPaper.MaxQuestions) EditorGUILayout.HelpBox("Only the first " + ExamPaper.MaxQuestions + " questions are used.", MessageType.Warning);
        foreach (var q in paper.questions)
            if (q.answers.Count > ExamPaper.MaxAnswers) { EditorGUILayout.HelpBox("A question has more than " + ExamPaper.MaxAnswers + " answers: only the first " + ExamPaper.MaxAnswers + " are shown.", MessageType.Warning); break; }
        serializedObject.ApplyModifiedProperties();
    }
}
