using System.IO;
using System.Linq;
using Mindscape.Data;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

/// <summary>
/// Mindscape › Story › New Chapter…: makes a chapter (Chapter 4 and later) as a StoryChapter asset in
/// Assets/Resources/Chapters/: its number, name, description and picture. Everything else (episodes, locations,
/// briefings, pictures per episode) is edited in that asset's Inspector. The main menu, loading screen, progress and
/// journal pick it up by themselves.
/// </summary>
public class NewChapterWindow : EditorWindow
{
    public const string Folder = "Assets/Resources/" + StoryChapters.ResourcesFolder;
    public const string ImageFolder = Folder + "/Images";

    int number;
    string chapterName = "New Beginnings", description = "";
    Texture2D thumbnail;
    bool firstEpisode = true;

    [MenuItem("Mindscape/Story/New Chapter…", priority = 1)]
    public static void Open() => GetWindow<NewChapterWindow>(true, "New Chapter").minSize = new Vector2(440, 360);

    void OnEnable()
    {
        StoryChapters.Reload();
        number = Mathf.Max(StoryChapters.FirstNumber, StoryChapters.All.Select(c => c.number + 1).DefaultIfEmpty(StoryChapters.FirstNumber).Max());
    }

    string AssetPath => Folder + "/Chapter " + number + ".asset";

    void OnGUI()
    {
        EditorGUILayout.HelpBox("Makes a new chapter. Chapters 1–3 are already in the game, so new chapters start at 4. After this, add episodes with New Episode and edit everything else in the chapter's Inspector.", MessageType.Info);
        number = Mathf.Max(StoryChapters.FirstNumber, EditorGUILayout.IntField("Chapter number", number));
        chapterName = EditorGUILayout.TextField(new GUIContent("Chapter name", "For example \"New Beginnings\". Shown on the chapter card, the loading screen and the journal."), chapterName);
        EditorGUILayout.LabelField("Description");
        description = EditorGUILayout.TextArea(description, GUILayout.MinHeight(44));

        EditorGUILayout.Space();
        EditorGUILayout.LabelField("Picture (chapter card and loading screen)", EditorStyles.boldLabel);
        using (new EditorGUILayout.HorizontalScope())
        {
            thumbnail = (Texture2D)EditorGUILayout.ObjectField(thumbnail, typeof(Texture2D), false, GUILayout.Width(120), GUILayout.Height(68));
            using (new EditorGUILayout.VerticalScope())
            {
                if (GUILayout.Button("Import image from your computer…")) Import();
                EditorGUILayout.LabelField("A wide picture (16:9), PNG or JPG. Or drag one from the Project window into the box.", EditorStyles.wordWrappedMiniLabel);
            }
        }

        EditorGUILayout.Space();
        firstEpisode = EditorGUILayout.ToggleLeft("Make Episode 1 of this chapter right after", firstEpisode);
        EditorGUILayout.Space();
        EditorGUILayout.LabelField("Chapter asset", AssetPath);

        int previous = number - 1;
        string problem = StoryChapters.All.Any(c => c.number == number) ? "Chapter " + number + " already exists." :
            string.IsNullOrWhiteSpace(chapterName) ? "Give the chapter a name." : null;
        string warning = previous >= StoryChapters.FirstNumber && !StoryChapters.All.Any(c => c.number == previous)
            ? "There is no Chapter " + previous + " yet. Players only reach Chapter " + number + " once Chapter " + previous + " exists." : null;
        if (problem != null) EditorGUILayout.HelpBox(problem, MessageType.Warning);
        else if (warning != null) EditorGUILayout.HelpBox(warning, MessageType.Warning);
        using (new EditorGUI.DisabledScope(problem != null))
            if (GUILayout.Button("Create Chapter", GUILayout.Height(28))) Create();
    }

    // Copies a picture from anywhere on the computer into the project and uses it.
    void Import()
    {
        string source = EditorUtility.OpenFilePanel("Choose the chapter picture", "", "png,jpg,jpeg");
        if (string.IsNullOrEmpty(source)) return;
        var imported = ImportImage(source, "Chapter " + number);
        if (imported != null) thumbnail = imported;
    }

    /// <summary>Copies an image file into Assets/Resources/Chapters/Images and returns it as a texture.</summary>
    public static Texture2D ImportImage(string source, string baseName)
    {
        Directory.CreateDirectory(ImageFolder);
        string path = AssetDatabase.GenerateUniqueAssetPath(ImageFolder + "/" + baseName + Path.GetExtension(source).ToLowerInvariant());
        File.Copy(source, path);
        AssetDatabase.ImportAsset(path);
        if (AssetImporter.GetAtPath(path) is TextureImporter importer)
        {
            importer.textureType = TextureImporterType.Default;
            importer.mipmapEnabled = false;
            importer.maxTextureSize = 2048;
            importer.SaveAndReimport();
        }
        return AssetDatabase.LoadAssetAtPath<Texture2D>(path);
    }

    void Create()
    {
        Directory.CreateDirectory(Folder);
        var chapter = CreateInstance<StoryChapter>();
        chapter.number = number;
        chapter.title = chapterName.Trim();
        chapter.description = description.Trim();
        chapter.thumbnail = thumbnail;
        AssetDatabase.CreateAsset(chapter, AssetPath);
        AssetDatabase.SaveAssets();
        StoryChapters.Reload();
        Selection.activeObject = chapter;
        EditorGUIUtility.PingObject(chapter);
        Debug.Log("[New Chapter] Made " + AssetPath + ". Add its episodes with Mindscape › Story › New Episode…");
        Close();
        if (firstEpisode) NewEpisodeWindow.Open(number, 1);
    }
}

/// <summary>
/// The Inspector of a chapter asset: the fields, then whether players can reach the chapter, a row per episode (with
/// its scene, and a button to open it), and a button that makes the next episode.
/// </summary>
[CustomEditor(typeof(StoryChapter))]
public class StoryChapterInspector : Editor
{
    public override void OnInspectorGUI()
    {
        var chapter = (StoryChapter)target;
        DrawDefaultInspector();
        EditorGUILayout.Space(10);
        EditorGUILayout.LabelField("In the game", EditorStyles.boldLabel);

        StoryChapters.Reload();
        bool playable = StoryChapters.Playable.Contains(chapter);
        var sameNumber = StoryChapters.All.Where(c => c.number == chapter.number && c != chapter).ToList();
        if (!AssetDatabase.GetAssetPath(chapter).StartsWith(NewChapterWindow.Folder + "/"))
            EditorGUILayout.HelpBox("This asset must be in " + NewChapterWindow.Folder + " for the game to find it.", MessageType.Error);
        else if (sameNumber.Count > 0)
            EditorGUILayout.HelpBox("Another chapter asset also has number " + chapter.number + ": " + sameNumber[0].name + ".", MessageType.Error);
        else if (chapter.episodes.Count == 0)
            EditorGUILayout.HelpBox("No episodes yet: the chapter is hidden from the game until it has one. Click the button below.", MessageType.Warning);
        else if (!playable)
            EditorGUILayout.HelpBox("Players cannot reach this chapter: Chapter " + (chapter.number - 1) + " is missing or has no episodes.", MessageType.Warning);
        else
            EditorGUILayout.HelpBox("In the game as Chapter " + chapter.number + " · " + chapter.title + ", with " + chapter.episodes.Count + " episode" + (chapter.episodes.Count == 1 ? "" : "s") + ". It unlocks when Chapter " + (chapter.number - 1) + " is finished.", MessageType.Info);

        var buildScenes = EditorBuildSettings.scenes.Where(s => s.enabled).Select(s => System.IO.Path.GetFileNameWithoutExtension(s.path)).ToList();
        for (int i = 0; i < chapter.episodes.Count; i++)
        {
            var e = chapter.episodes[i];
            string path = AssetDatabase.FindAssets("t:Scene " + e.scene).Select(AssetDatabase.GUIDToAssetPath).FirstOrDefault(p => System.IO.Path.GetFileNameWithoutExtension(p) == e.scene);
            using (new EditorGUILayout.HorizontalScope())
            {
                EditorGUILayout.LabelField("Episode " + (i + 1), string.IsNullOrEmpty(e.title) ? "(no title)" : e.title);
                using (new EditorGUI.DisabledScope(path == null))
                    if (GUILayout.Button("Open scene", GUILayout.Width(90)) && EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo())
                        EditorSceneManager.OpenScene(path);
            }
            if (string.IsNullOrEmpty(e.scene)) EditorGUILayout.HelpBox("Episode " + (i + 1) + " has no scene.", MessageType.Warning);
            else if (path == null) EditorGUILayout.HelpBox("Episode " + (i + 1) + ": there is no scene called \"" + e.scene + "\".", MessageType.Warning);
            else if (!buildScenes.Contains(e.scene)) EditorGUILayout.HelpBox("Episode " + (i + 1) + ": \"" + e.scene + "\" is not in File › Build Profiles, so it will not be in a build.", MessageType.Warning);
        }

        EditorGUILayout.Space(6);
        if (GUILayout.Button("Make Episode " + (chapter.episodes.Count + 1) + " of this chapter…", GUILayout.Height(26)))
            NewEpisodeWindow.Open(chapter.number, chapter.episodes.Count + 1);
    }
}
