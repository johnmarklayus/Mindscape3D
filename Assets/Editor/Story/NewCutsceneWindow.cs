using System.Collections.Generic;
using System.IO;
using System.Linq;
using Mindscape.Cutscenes;
using Mindscape.Data;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

/// <summary>
/// Mindscape › Story › New Cutscene…: picks pictures from the computer, makes one slide per picture in a new cutscene
/// asset (Assets/Story/Cutscenes/[name]/), and can hook it up right away: before an episode of a chapter made in the
/// editor, or as a scene of its own. The words, speakers and timing are then edited in the asset's Inspector.
/// </summary>
public class NewCutsceneWindow : EditorWindow
{
    public const string Root = "Assets/Story/Cutscenes";
    enum Use { [InspectorName("Nothing yet (I will use it from a cinematic)")] Nothing, [InspectorName("Before an episode")] BeforeEpisode, [InspectorName("As a scene of its own")] OwnScene }

    string cutsceneName = "Morning";
    readonly List<string> pictures = new List<string>();
    Use use = Use.BeforeEpisode;
    int chapterIndex, episodeIndex;
    string nextScene = "";
    Vector2 scroll;

    [MenuItem("Mindscape/Story/New Cutscene…", priority = 3)]
    public static void Open() => GetWindow<NewCutsceneWindow>(true, "New Cutscene").minSize = new Vector2(460, 420);

    string Folder => Root + "/" + cutsceneName.Trim();

    void OnGUI()
    {
        EditorGUILayout.HelpBox("A cutscene is a row of pictures with words, shown full screen. Pick the pictures here (one slide each); write the words in the Inspector afterwards.", MessageType.Info);
        cutsceneName = EditorGUILayout.TextField(new GUIContent("Name", "For example \"Morning\". Only for you: players do not see it."), cutsceneName);

        EditorGUILayout.Space();
        EditorGUILayout.LabelField("Pictures (one slide each, in this order)", EditorStyles.boldLabel);
        using (new EditorGUILayout.HorizontalScope())
        {
            if (GUILayout.Button("Add a picture…"))
            {
                string p = EditorUtility.OpenFilePanel("Choose a picture", "", "png,jpg,jpeg");
                if (!string.IsNullOrEmpty(p)) pictures.Add(p);
            }
            if (GUILayout.Button("Add every picture in a folder…"))
            {
                string dir = EditorUtility.OpenFolderPanel("Choose the folder with the pictures", "", "");
                if (!string.IsNullOrEmpty(dir))
                    pictures.AddRange(Directory.GetFiles(dir).Where(f => new[] { ".png", ".jpg", ".jpeg" }.Contains(Path.GetExtension(f).ToLowerInvariant())).OrderBy(f => f));
            }
        }
        scroll = EditorGUILayout.BeginScrollView(scroll, GUILayout.MinHeight(80), GUILayout.MaxHeight(160));
        for (int i = 0; i < pictures.Count; i++)
            using (new EditorGUILayout.HorizontalScope())
            {
                EditorGUILayout.LabelField("Slide " + (i + 1), Path.GetFileName(pictures[i]));
                if (GUILayout.Button("↑", GUILayout.Width(24)) && i > 0) { (pictures[i - 1], pictures[i]) = (pictures[i], pictures[i - 1]); }
                if (GUILayout.Button("✕", GUILayout.Width(24))) { pictures.RemoveAt(i); break; }
            }
        if (pictures.Count == 0) EditorGUILayout.LabelField("No pictures yet. You can also add slides later in the Inspector.", EditorStyles.wordWrappedMiniLabel);
        EditorGUILayout.EndScrollView();

        EditorGUILayout.Space();
        use = (Use)EditorGUILayout.EnumPopup("Use it", use);
        var chapters = StoryChapters.All;
        if (use == Use.BeforeEpisode)
        {
            if (chapters.Length == 0) EditorGUILayout.HelpBox("There are no chapters made in the editor yet (Mindscape › Story › New Chapter…). Chapters 1–3 can play a cutscene from a cinematic instead.", MessageType.Warning);
            else
            {
                chapterIndex = Mathf.Clamp(EditorGUILayout.Popup("Chapter", chapterIndex, chapters.Select(c => "Chapter " + c.number + " · " + c.title).ToArray()), 0, chapters.Length - 1);
                var eps = chapters[chapterIndex].episodes;
                if (eps.Count == 0) EditorGUILayout.HelpBox("This chapter has no episodes yet.", MessageType.Warning);
                else episodeIndex = Mathf.Clamp(EditorGUILayout.Popup("Episode", episodeIndex, eps.Select((e, i) => "Episode " + (i + 1) + " · " + e.title).ToArray()), 0, eps.Count - 1);
            }
        }
        else if (use == Use.OwnScene)
            nextScene = EditorGUILayout.TextField(new GUIContent("Then open scene", "The scene after the cutscene, for example \"Chapter 4 - Episode 1\". Empty: the main menu."), nextScene);

        EditorGUILayout.Space();
        EditorGUILayout.LabelField("Saved in", Folder + "/" + cutsceneName.Trim() + ".asset");
        string problem = string.IsNullOrWhiteSpace(cutsceneName) ? "Give the cutscene a name." :
            cutsceneName.IndexOfAny(Path.GetInvalidFileNameChars()) >= 0 ? "The name cannot contain / \\ : * ? \" < > |" :
            File.Exists(Folder + "/" + cutsceneName.Trim() + ".asset") ? "A cutscene with that name already exists." :
            use == Use.BeforeEpisode && (chapters.Length == 0 || chapters[chapterIndex].episodes.Count == 0) ? "Pick an episode, or choose another \"Use it\"." : null;
        if (problem != null) EditorGUILayout.HelpBox(problem, MessageType.Warning);
        using (new EditorGUI.DisabledScope(problem != null))
            if (GUILayout.Button("Create Cutscene", GUILayout.Height(28))) Create();
    }

    void Create()
    {
        string name = cutsceneName.Trim();
        Directory.CreateDirectory(Folder);
        var cutscene = CreateInstance<CutsceneAsset>();
        for (int i = 0; i < pictures.Count; i++)
            cutscene.slides.Add(new CutsceneSlide { image = ImportPicture(pictures[i], Folder + "/Slide " + (i + 1)) });
        if (cutscene.slides.Count == 0) cutscene.slides.Add(new CutsceneSlide());
        cutscene.nextScene = use == Use.OwnScene ? nextScene.Trim() : "";
        string path = Folder + "/" + name + ".asset";
        AssetDatabase.CreateAsset(cutscene, path);

        if (use == Use.BeforeEpisode)
        {
            var chapter = StoryChapters.All[chapterIndex];
            Undo.RecordObject(chapter, "Cutscene before episode");
            chapter.episodes[episodeIndex].cutsceneBefore = cutscene;
            EditorUtility.SetDirty(chapter);
            Debug.Log("[New Cutscene] Plays before Chapter " + chapter.number + " · Episode " + (episodeIndex + 1) + " (" + chapter.name + " › Episodes › Cutscene Before).");
        }
        AssetDatabase.SaveAssets();
        if (use == Use.OwnScene) MakeScene(cutscene, name);
        Selection.activeObject = cutscene;
        EditorGUIUtility.PingObject(cutscene);
        Debug.Log("[New Cutscene] Made " + path + " with " + cutscene.slides.Count + " slide(s). Write the words in its Inspector.");
        Close();
    }

    /// <summary>Copies a picture into the project (as a texture for the cutscene) and returns it.</summary>
    public static Texture2D ImportPicture(string source, string pathWithoutExtension)
    {
        string path = AssetDatabase.GenerateUniqueAssetPath(pathWithoutExtension + Path.GetExtension(source).ToLowerInvariant());
        File.Copy(source, path);
        AssetDatabase.ImportAsset(path);
        if (AssetImporter.GetAtPath(path) is TextureImporter importer)
        {
            importer.textureType = TextureImporterType.Default; importer.mipmapEnabled = false; importer.maxTextureSize = 2048; importer.npotScale = TextureImporterNPOTScale.None;
            importer.SaveAndReimport();
        }
        return AssetDatabase.LoadAssetAtPath<Texture2D>(path);
    }

    // A scene with only a camera and the cutscene: it plays, then opens Next Scene.
    static void MakeScene(CutsceneAsset cutscene, string name)
    {
        if (!EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo()) return;
        var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
        var cam = new GameObject("Main Camera").AddComponent<Camera>();
        cam.tag = "MainCamera"; cam.clearFlags = CameraClearFlags.SolidColor; cam.backgroundColor = Color.black;
        var player = new GameObject("Cutscene").AddComponent<CutsceneScene>();
        player.cutscene = cutscene;
        string path = AssetDatabase.GenerateUniqueAssetPath("Assets/Scenes/Cutscene - " + name + ".unity");
        EditorSceneManager.SaveScene(scene, path);
        var list = EditorBuildSettings.scenes.ToList();
        if (!list.Any(s => s.path == path)) { list.Add(new EditorBuildSettingsScene(path, true)); EditorBuildSettings.scenes = list.ToArray(); }
        foreach (var guid in AssetDatabase.FindAssets("t:BuildProfile"))
        {
            var profile = AssetDatabase.LoadAssetAtPath<UnityEditor.Build.Profile.BuildProfile>(AssetDatabase.GUIDToAssetPath(guid));
            if (profile == null || !profile.overrideGlobalScenes || profile.scenes.Any(s => s.path == path)) continue;
            profile.scenes = profile.scenes.Concat(new[] { new EditorBuildSettingsScene(path, true) }).ToArray();
            EditorUtility.SetDirty(profile);
        }
        AssetDatabase.SaveAssets();
        Debug.Log("[New Cutscene] Made the scene " + path + " (in the build list). Something must open it: set it as an episode's next scene, or a menu button.");
    }
}

/// <summary>The cutscene asset's Inspector: the slides, then buttons to add pictures and to see which slides lack something.</summary>
[CustomEditor(typeof(CutsceneAsset))]
public class CutsceneAssetInspector : Editor
{
    public override void OnInspectorGUI()
    {
        var cutscene = (CutsceneAsset)target;
        EditorGUILayout.HelpBox("Each slide: a picture, who speaks (empty = narration) and the words. Auto Advance Seconds 0 waits for the player. Drag the ☰ handle to reorder.", MessageType.Info);
        DrawDefaultInspector();
        EditorGUILayout.Space(6);
        using (new EditorGUILayout.HorizontalScope())
        {
            if (GUILayout.Button("Add a slide from a picture…"))
            {
                string p = EditorUtility.OpenFilePanel("Choose a picture", "", "png,jpg,jpeg");
                if (!string.IsNullOrEmpty(p))
                {
                    string folder = Path.GetDirectoryName(AssetDatabase.GetAssetPath(cutscene)).Replace('\\', '/');
                    var tex = NewCutsceneWindow.ImportPicture(p, folder + "/Slide " + (cutscene.slides.Count + 1));
                    Undo.RecordObject(cutscene, "Add slide");
                    cutscene.slides.Add(new CutsceneSlide { image = tex });
                    EditorUtility.SetDirty(cutscene);
                }
            }
        }
        for (int i = 0; i < cutscene.slides.Count; i++)
        {
            var s = cutscene.slides[i];
            if (s.image == null && string.IsNullOrWhiteSpace(s.text)) EditorGUILayout.HelpBox("Slide " + (i + 1) + " is empty (no picture, no words).", MessageType.Warning);
        }
        // Where it is used.
        var users = StoryChapters.All.SelectMany(c => c.episodes.Select((e, i) => (c, e, i))).Where(x => x.e.cutsceneBefore == cutscene).ToList();
        foreach (var (c, e, i) in users) EditorGUILayout.HelpBox("Plays before Chapter " + c.number + " · Episode " + (i + 1) + " (" + e.title + ").", MessageType.None);
    }
}
