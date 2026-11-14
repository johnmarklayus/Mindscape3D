using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using Mindscape.AcademicPressure;
using UnityEditor;
using UnityEngine;

/// <summary>
/// Mindscape › Story › Edit Dialogue Words: every line the Chapter 1–3 scripts show, in one asset, with a search box.
/// Find every line reads the scripts again (after a script changes) and keeps what was already changed.
/// </summary>
[CustomEditor(typeof(StoryWords))]
public class StoryWordsEditor : Editor
{
    const string AssetPath = "Assets/Resources/" + StoryWords.ResourcePath + ".asset";
    static readonly string[] Folders = { "Assets/Scripts/Chapters/Chapter 1 - Academic Pressure", "Assets/Scripts/Chapters/Chapter 2 - Family Expectations", "Assets/Scripts/Chapters/Chapter 3 - Social Dynamics" };
    static readonly Regex Wrapped = new Regex("\\bW\\(\"((?:[^\"\\\\]|\\\\.)*)\"\\)");

    string search = "";
    static string group = "Everything";

    /// <summary>Selects the Dialogue Words asset showing one part of the story ("Chapter 2", or "Chapter 2 · Family Exam").</summary>
    public static void OpenAt(string part)
    {
        Open();
        group = string.IsNullOrEmpty(part) ? "Everything" : part;
    }

    /// <summary>The part of the story an episode's script belongs to, as the list names it ("Chapter 1 · House").</summary>
    public static string PartOf(MonoBehaviour episode)
    {
        var script = episode != null ? MonoScript.FromMonoBehaviour(episode) : null;
        string path = script != null ? AssetDatabase.GetAssetPath(script) : "";
        return path.Length > 0 ? GroupName(Path.GetDirectoryName(path), path) : "";
    }
    bool onlyChanged;
    int page;
    const int PerPage = 30;
    Vector2 scroll;

    [MenuItem("Mindscape/Story/Edit Dialogue Words (Chapters 1-3)", priority = 6)]
    public static void Open()
    {
        var words = AssetDatabase.LoadAssetAtPath<StoryWords>(AssetPath);
        if (words == null)
        {
            Directory.CreateDirectory(Path.GetDirectoryName(AssetPath));
            words = CreateInstance<StoryWords>();
            AssetDatabase.CreateAsset(words, AssetPath);
        }
        int added = Scan(words);
        AssetDatabase.SaveAssets();
        Selection.activeObject = words;
        EditorGUIUtility.PingObject(words);
        Debug.Log("[Dialogue Words] " + words.entries.Count + " lines (" + added + " new). Edit the Changed box of a line; empty keeps the script's words.");
    }

    /// <summary>Reads the chapter scripts and adds every W("...") line not yet in the asset. Returns how many were added.</summary>
    public static int Scan(StoryWords words)
    {
        var known = new Dictionary<string, StoryWords.Entry>();
        foreach (var e in words.entries) if (!known.ContainsKey(e.original)) known[e.original] = e;
        foreach (var e in words.entries) e.missing = true;
        int added = 0;
        Undo.RecordObject(words, "Find every line");
        foreach (var folder in Folders)
        {
            if (!Directory.Exists(folder)) continue;
            foreach (var file in Directory.GetFiles(folder, "*.cs").OrderBy(f => f))
            {
                string groupName = GroupName(folder, file);
                var lines = File.ReadAllLines(file);
                for (int i = 0; i < lines.Length; i++)
                {
                    if (lines[i].TrimStart().StartsWith("//")) continue;
                    foreach (Match m in Wrapped.Matches(lines[i]))
                    {
                        string original;
                        try { original = Regex.Unescape(m.Groups[1].Value); } catch { original = m.Groups[1].Value; }
                        string where = Path.GetFileName(file) + ":" + (i + 1);
                        if (known.TryGetValue(original, out var entry)) { entry.missing = false; entry.where = where; entry.group = groupName; continue; }
                        entry = new StoryWords.Entry { original = original, where = where, group = groupName };
                        words.entries.Add(entry); known[original] = entry; added++;
                    }
                }
            }
        }
        EditorUtility.SetDirty(words);
        return added;
    }

    static string GroupName(string folder, string file)
    {
        string chapter = Path.GetFileName(folder).Split('-')[0].Trim();   // "Chapter 1"
        string script = Path.GetFileNameWithoutExtension(file);
        return chapter + " · " + ObjectNames.NicifyVariableName(script).Replace(" Episode", "");
    }

    public override void OnInspectorGUI()
    {
        var words = (StoryWords)target;
        serializedObject.Update();
        EditorGUILayout.HelpBox("Every line the Chapter 1–3 scripts show. Type in Changed to show other words; leave it empty to keep the script's words. \"Joey\" is replaced by the player's name.\n\nA line made of parts (with a name or an earlier answer in between) appears as its parts. Lines in Chapter 4 and later are written in cinematics and conversations instead.", MessageType.Info);
        using (new EditorGUILayout.HorizontalScope())
        {
            if (GUILayout.Button(new GUIContent("Find every line", "Reads the scripts again (after a script changed). Changed words are kept."))) { int n = Scan(words); Debug.Log("[Dialogue Words] " + n + " new line(s)."); }
            if (GUILayout.Button(new GUIContent("Clear lines no longer in a script", "Removes lines that were deleted from the scripts.")))
            {
                Scan(words);
                Undo.RecordObject(words, "Clear old lines");
                words.entries.RemoveAll(e => e.missing);
                EditorUtility.SetDirty(words);
            }
        }
        var groups = new List<string> { "Everything" };
        foreach (var g in words.entries.Select(e => e.group).Where(g => !string.IsNullOrEmpty(g)).Distinct())
        {
            string chapter = g.Split('·')[0].Trim();
            if (!groups.Contains(chapter)) groups.Add(chapter);
            groups.Add(g);
        }
        if (!groups.Contains(group)) group = "Everything";
        int gi = Mathf.Max(0, groups.IndexOf(group));
        using (new EditorGUILayout.HorizontalScope())
        {
            int picked = EditorGUILayout.Popup(gi, groups.Select(g => g.Contains("·") ? "    " + g : g).ToArray(), GUILayout.MaxWidth(260)); if (picked != gi) page = 0; group = groups[picked];
            onlyChanged = GUILayout.Toggle(onlyChanged, "Only changed", GUILayout.Width(100));
        }
        search = EditorGUILayout.TextField("Search", search);

        var shown = new List<int>();
        for (int i = 0; i < words.entries.Count; i++)
        {
            var e = words.entries[i];
            if (group != "Everything" && e.group != group && !(e.group ?? "").StartsWith(group + " ·")) continue;
            if (onlyChanged && string.IsNullOrEmpty(e.changed)) continue;
            if (search.Length > 0 && (e.original + " " + e.changed + " " + e.where).IndexOf(search, System.StringComparison.OrdinalIgnoreCase) < 0) continue;
            shown.Add(i);
        }
        int pages = Mathf.Max(1, (shown.Count + PerPage - 1) / PerPage);
        page = Mathf.Clamp(page, 0, pages - 1);
        using (new EditorGUILayout.HorizontalScope())
        {
            EditorGUILayout.LabelField(shown.Count + " line(s), " + words.entries.Count(e => !string.IsNullOrEmpty(e.changed)) + " changed", EditorStyles.miniBoldLabel);
            using (new EditorGUI.DisabledScope(page == 0)) if (GUILayout.Button("◀", GUILayout.Width(28))) page--;
            GUILayout.Label((page + 1) + " / " + pages, GUILayout.Width(50));
            using (new EditorGUI.DisabledScope(page >= pages - 1)) if (GUILayout.Button("▶", GUILayout.Width(28))) page++;
        }

        var list = serializedObject.FindProperty("entries");
        foreach (int i in shown.Skip(page * PerPage).Take(PerPage))
        {
            var e = words.entries[i];
            var item = list.GetArrayElementAtIndex(i);
            using (new EditorGUILayout.VerticalScope(EditorStyles.helpBox))
            {
                EditorGUILayout.LabelField(e.group + "   ·   " + e.where + (e.missing ? "   (no longer in the script)" : ""), EditorStyles.miniLabel);
                using (new EditorGUI.DisabledScope(true))
                    EditorGUILayout.TextArea(e.original, new GUIStyle(EditorStyles.textArea) { wordWrap = true });
                var changed = item.FindPropertyRelative("changed");
                EditorGUILayout.LabelField("Changed", EditorStyles.miniBoldLabel);
                changed.stringValue = EditorGUILayout.TextArea(changed.stringValue, new GUIStyle(EditorStyles.textArea) { wordWrap = true });
                using (new EditorGUILayout.HorizontalScope())
                {
                    if (GUILayout.Button("Copy the original into Changed", EditorStyles.miniButton)) changed.stringValue = e.original;
                    using (new EditorGUI.DisabledScope(string.IsNullOrEmpty(changed.stringValue)))
                        if (GUILayout.Button("Undo the change", EditorStyles.miniButton)) changed.stringValue = "";
                }
            }
        }
        serializedObject.ApplyModifiedProperties();
    }
}
