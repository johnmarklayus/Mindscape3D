using System;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using Mindscape.AcademicPressure;
using Mindscape.Data;
using UnityEditor;
using UnityEditor.Callbacks;
using UnityEditor.SceneManagement;
using UnityEngine;

/// <summary>
/// Mindscape › Story › New Episode: makes a new episode scene from an existing one (the house, the school, the reunion
/// hall… with the city, lighting, player and camera already set up) instead of generating it from code.
///   Keep the template's story  an exact copy, story included: change it in the Inspector and the Scene view.
///   New story script           also writes a starter episode script (Assets/Scripts/Chapters/Chapter N/…) and, once
///                              Unity has compiled it, puts it in the new scene in place of the template's story.
/// The scene is added to the build list and, for Chapter 4 and later, to the chapter asset's Episodes list (which is
/// what puts it in the main menu and on the loading screen). See the Onboarding page "Create an episode".
/// </summary>
public class NewEpisodeWindow : EditorWindow
{
    int chapter = 4, episode = 1, template;
    string episodeTitle = "First Steps", className = "";
    bool newScript = true;
    string[] scenes;

    [MenuItem("Mindscape/Story/New Episode…", priority = 0)]
    static void OpenMenu() => Open(0, 0);

    /// <summary>Opens the window; chapter 0 picks the last chapter made in the editor and its next episode.</summary>
    public static void Open(int chapter, int episode)
    {
        var window = GetWindow<NewEpisodeWindow>(true, "New Episode");
        window.minSize = new Vector2(440, 340);
        StoryChapters.Reload();
        if (chapter == 0)
        {
            var last = StoryChapters.All.LastOrDefault();
            chapter = last != null ? last.number : StoryChapters.FirstNumber;
            episode = last != null ? last.episodes.Count + 1 : 1;
        }
        window.chapter = chapter; window.episode = Mathf.Max(1, episode);
        window.episodeTitle = "New Episode"; window.className = "";
    }

    StoryChapter ChapterAsset => StoryChapters.All.FirstOrDefault(c => c.number == chapter);

    void OnEnable()
    {
        scenes = Directory.GetFiles("Assets/Scenes", "*.unity").Select(p => p.Replace('\\', '/'))
            .Where(p => Path.GetFileNameWithoutExtension(p).StartsWith("Chapter") || p.EndsWith("Tutorial.unity")).OrderBy(p => p).ToArray();
        int house = Array.FindIndex(scenes, p => p.EndsWith("Chapter 3 - Episode 7.unity"));
        if (house >= 0) template = house;
    }

    string ScenePath => "Assets/Scenes/Chapter " + chapter + " - Episode " + episode + ".unity";
    string ClassName => string.IsNullOrWhiteSpace(className) ? DefaultClass() : className.Trim();
    string DefaultClass() => "Chapter" + chapter + "Episode" + episode + Regex.Replace(episodeTitle ?? "", "[^A-Za-z0-9]", "");
    string ScriptPath => "Assets/Scripts/Chapters/Chapter " + chapter + "/" + ClassName + ".cs";

    void OnGUI()
    {
        EditorGUILayout.HelpBox("Copies an existing episode scene (its place, lighting, player and camera) into a new episode. Pick the template that looks most like where the new episode happens.", MessageType.Info);
        chapter = EditorGUILayout.IntField("Chapter", Mathf.Max(1, chapter));
        episode = EditorGUILayout.IntField("Episode", Mathf.Max(1, episode));
        var chapterAsset = ChapterAsset;
        if (chapter >= StoryChapters.FirstNumber && chapterAsset == null)
        {
            EditorGUILayout.HelpBox("There is no Chapter " + chapter + " yet. Make the chapter first, so this episode is added to it and shows in the main menu.", MessageType.Warning);
            if (GUILayout.Button("Make Chapter " + chapter + " first…")) { NewChapterWindow.Open(); Close(); return; }
        }
        else if (chapterAsset != null)
            EditorGUILayout.LabelField("Adds to", chapterAsset.name + " · " + chapterAsset.title + " (as Episode " + episode + ")");
        episodeTitle = EditorGUILayout.TextField("Title", episodeTitle);
        template = EditorGUILayout.Popup("Template scene", template, scenes.Select(Path.GetFileNameWithoutExtension).ToArray());
        newScript = EditorGUILayout.Toggle(new GUIContent("New story script", "Off: keep the template's story (an exact copy). On: start from a short starter script."), newScript);
        if (newScript) className = EditorGUILayout.TextField("Script class", string.IsNullOrWhiteSpace(className) ? DefaultClass() : className);

        EditorGUILayout.Space();
        EditorGUILayout.LabelField("Scene", ScenePath);
        if (newScript) EditorGUILayout.LabelField("Script", ScriptPath);

        string problem = File.Exists(ScenePath) ? "That scene already exists." :
            newScript && !Regex.IsMatch(ClassName, "^[A-Za-z_][A-Za-z0-9_]*$") ? "The script class must be a C# name (letters and digits)." :
            newScript && File.Exists(ScriptPath) ? "That script already exists." : null;
        if (problem != null) EditorGUILayout.HelpBox(problem, MessageType.Warning);
        using (new EditorGUI.DisabledScope(problem != null || scenes.Length == 0))
            if (GUILayout.Button("Create Episode", GUILayout.Height(28))) { Create(); Close(); }
    }

    void Create()
    {
        if (!EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo()) return;
        if (!AssetDatabase.CopyAsset(scenes[template], ScenePath)) { Debug.LogError("[New Episode] Could not copy " + scenes[template]); return; }
        AddToBuild(ScenePath);
        AddToChapter(chapter, episode, episodeTitle, Path.GetFileNameWithoutExtension(ScenePath));
        if (!newScript)
        {
            EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            Debug.Log("[New Episode] " + ScenePath + " is a copy of " + Path.GetFileNameWithoutExtension(scenes[template]) + ", story included.");
            return;
        }
        Directory.CreateDirectory(Path.GetDirectoryName(ScriptPath));
        File.WriteAllText(ScriptPath, StarterScript(ClassName, chapter, episode, episodeTitle));
        SessionState.SetString(PendingKey, ScenePath + "|" + ClassName + "|" + episodeTitle + "|" + chapter + "|" + episode);
        AssetDatabase.Refresh();   // compiles the script; AttachPending runs after the reload
        Debug.Log("[New Episode] Wrote " + ScriptPath + ". The scene opens with it once Unity has compiled it.");
    }

    // ---------------------------------------------------------------- after the new script compiles

    const string PendingKey = "Mindscape.NewEpisode.Pending";

    [DidReloadScripts]
    static void AttachPending()
    {
        string pending = SessionState.GetString(PendingKey, "");
        if (pending == "") return;
        SessionState.EraseString(PendingKey);
        EditorApplication.delayCall += () => Attach(pending.Split('|'));
    }

    static void Attach(string[] p)
    {
        string scenePath = p[0], typeName = p[1], title = p[2];
        var type = AppDomain.CurrentDomain.GetAssemblies().Select(a => a.GetType("Mindscape.Story." + typeName)).FirstOrDefault(t => t != null);
        if (type == null) { Debug.LogError("[New Episode] " + typeName + " did not compile; fix the Console errors, then add it to the scene by hand."); return; }
        var scene = EditorSceneManager.OpenScene(scenePath, OpenSceneMode.Single);
        var old = UnityEngine.Object.FindFirstObjectByType<AcademicEpisode>(FindObjectsInactive.Include);
        var root = new GameObject("Episode - " + title);
        var episode = (AcademicEpisode)root.AddComponent(type);
        Transform player = old != null ? old.player : GameObject.Find("Player")?.transform;
        Camera camera = old != null ? old.storyCamera : Camera.main;
        episode.player = player; episode.storyCamera = camera;
        // Start where the template started, with the first shot from the template's camera.
        var spawn = new GameObject("Start").transform; spawn.SetParent(root.transform, false);
        if (player != null) spawn.SetPositionAndRotation(player.position, player.rotation);
        var view = new GameObject("Opening view").transform; view.SetParent(root.transform, false);
        if (camera != null) view.SetPositionAndRotation(camera.transform.position, camera.transform.rotation);
        var serialized = new SerializedObject(episode);
        serialized.FindProperty("spawn").objectReferenceValue = spawn;
        if (p.Length >= 5 && serialized.FindProperty("chapterNumber") != null)
        {
            serialized.FindProperty("chapterNumber").intValue = int.Parse(p[3]);
            serialized.FindProperty("episodeNumber").intValue = int.Parse(p[4]);
        }
        serialized.FindProperty("openingView").objectReferenceValue = view;
        serialized.ApplyModifiedPropertiesWithoutUndo();
        // The template's story goes; its objects (people, props, spots) stay, to reuse or delete.
        if (old != null)
        {
            Debug.Log("[New Episode] Removed the template's story (" + old.GetType().Name + " on " + old.name + "). Its objects are still in the scene: reuse them or delete them.");
            UnityEngine.Object.DestroyImmediate(old);
        }
        EditorSceneManager.MarkSceneDirty(scene);
        EditorSceneManager.SaveScene(scene);
        Selection.activeGameObject = root;
        Debug.Log("[New Episode] " + scenePath + " is ready with " + typeName + ". Add spots under '" + root.name + "' and write the story in the script.");
    }

    // The chapter asset's Episodes list: this episode's title and scene, at its place.
    static void AddToChapter(int chapter, int episode, string title, string scene)
    {
        var asset = StoryChapters.All.FirstOrDefault(c => c.number == chapter);
        if (asset == null) return;
        Undo.RecordObject(asset, "Add episode to chapter");
        while (asset.episodes.Count < episode) asset.episodes.Add(new StoryEpisodeInfo { title = "", scene = "" });
        var entry = asset.episodes[episode - 1];
        entry.title = title; entry.scene = scene;
        EditorUtility.SetDirty(asset);
        AssetDatabase.SaveAssets();
        StoryChapters.Reload();
        Debug.Log("[New Episode] Added to " + asset.name + " as Episode " + episode + ". Fill in its location, briefing and picture there.");
    }

    static void AddToBuild(string path)
    {
        var list = EditorBuildSettings.scenes.ToList();
        if (!list.Any(s => s.path == path)) list.Add(new EditorBuildSettingsScene(path, true));
        EditorBuildSettings.scenes = list.ToArray();
        foreach (var guid in AssetDatabase.FindAssets("t:BuildProfile"))
        {
            var profile = AssetDatabase.LoadAssetAtPath<UnityEditor.Build.Profile.BuildProfile>(AssetDatabase.GUIDToAssetPath(guid));
            if (profile == null || !profile.overrideGlobalScenes || profile.scenes.Any(s => s.path == path)) continue;
            profile.scenes = profile.scenes.Concat(new[] { new EditorBuildSettingsScene(path, true) }).ToArray();
            EditorUtility.SetDirty(profile);
        }
        AssetDatabase.SaveAssets();
    }

    public static string StarterScript(string className, int chapter, int episode, string title)
    {
        string safeTitle = (title ?? "").Replace("\\", "\\\\").Replace("\"", "\\\"");
        return
$@"using System.Collections;
using Mindscape.AcademicPressure;
using UnityEngine;

namespace Mindscape.Story
{{
    // Chapter {chapter} · Episode {episode} · {safeTitle}
    // Made with Mindscape › Story › New Episode. The places live in the scene (drag them in the Scene view); the order
    // of events and the words live here. The chapter and episode numbers, the time limit, the next scene and the save
    // are set by StoryEpisode from the Inspector and the chapter asset. See the Onboarding page, ""Create an episode"".
    public sealed class {className} : StoryEpisode
    {{
        [Header(""Scene points (drag them in the Scene view)"")]
        public Transform spawn;
        public Transform openingView;
        [Tooltip(""Places the player walks to, in order. Each gets an [E] prompt and the lines below."")]
        public Transform[] spots = new Transform[0];

        protected override IEnumerator Play()
        {{
            if (spawn != null) Teleport(spawn.position, spawn.eulerAngles.y);
            if (openingView != null) Shot(openingView.position, openingView.position + openingView.forward * 8);
            yield return Card(""CHAPTER {chapter}\n<size=60%>Episode {episode:00} · {safeTitle}</size>"");
            yield return Say(""Narration"", ""Write the opening line here."");

            // One stop per spot: walk there, press E, read the lines.
            for (int i = 0; i < spots.Length; i++)
            {{
                bool done = false;
                AddSpot(spots[i], ""Look"", () => !done, () => Stop(() => done = true));
                SetObjective(""{safeTitle}"", Check(false, ""Find the marked place""));
                yield return RoamUntil(() => done);
            }}

            // Free walking until every cinematic set to play at a place has played (Mindscape › Story › New Cinematic).
            yield return RoamUntilCinematicsDone();

            Complete(""{safeTitle}"", ""Write the closing words here."");
        }}

        IEnumerator Stop(System.Action done)
        {{
            yield return Think(""Something Joey thinks here."");
            yield return Me(""Something Joey says here."");
            done();
        }}
    }}
}}
";
    }
}
