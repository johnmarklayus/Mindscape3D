using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

/// <summary>
/// The Player's Inspector: with a Player Settings asset linked, the values that come from the asset are greyed out and
/// a button opens the asset, so nobody edits a value that the asset will replace when the game starts.
/// </summary>
[CustomEditor(typeof(PlayerMovement))]
public class PlayerMovementInspector : Editor
{
    public override void OnInspectorGUI()
    {
        serializedObject.Update();
        var settings = ((PlayerMovement)target).settings;
        if (settings != null)
        {
            EditorGUILayout.HelpBox("Movement, camera, zoom and crosshair come from \"" + settings.name + "\". Every scene linked to it changes together: edit the asset, not the greyed values here.", MessageType.Info);
            if (GUILayout.Button("Edit " + settings.name)) Selection.activeObject = settings;
        }
        var property = serializedObject.GetIterator();
        for (bool enter = true; property.NextVisible(enter); enter = false)
        {
            if (property.name == "m_Script") continue;
            using (new EditorGUI.DisabledScope(settings != null && PlayerSettings.Holds(property.name)))
                EditorGUILayout.PropertyField(property, true);
        }
        serializedObject.ApplyModifiedProperties();
    }
}

/// <summary>
/// One-time set-up (already run on 2026-11-13): makes a Player Settings asset for each group of scenes whose Player had
/// the same values, and links each scene's Player (and Player.prefab) to it. Nothing plays differently afterwards; the
/// values just live in one place per kind of place. Safe to re-run: linked players are left alone.
/// </summary>
public static class PlayerSettingsTools
{
    const string Folder = "Assets/Settings/Player";
    const string PrefabPath = "Assets/Prefabs/Player.prefab";

    // A readable name for each group, from a scene in it.
    static readonly Dictionary<string, string> Names = new Dictionary<string, string>
    {
        { "Player.prefab", "Default" },
        { "Chapter 1 - Episode 1", "House" },
        { "Chapter 1 - Episode 2", "School" },
        { "Chapter 3 - Episode 1", "House at Night" },
        { "Chapter 3 - Episode 2", "Reunion Hall" },
        { "Chapter 3 - Episode 4", "Reunion Hall Corner" },
        { "Tutorial", "Tutorial" },
    };

    static bool Matches(PlayerMovement movement)
    {
        var probe = ScriptableObject.CreateInstance<PlayerSettings>();
        probe.CopyFrom(movement);
        bool same = JsonUtility.ToJson(probe) == JsonUtility.ToJson(movement.settings);
        Object.DestroyImmediate(probe);
        return same;
    }

    [MenuItem("Mindscape/Story/Link Players to Shared Settings (All Scenes)", priority = 40)]
    static void Menu() => Debug.Log(LinkAll());

    public static string LinkAll()
    {
        if (!Application.isBatchMode && !EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo()) return "Cancelled.";
        Directory.CreateDirectory(Folder);
        // Values -> asset path (paths, not objects: opening a scene unloads assets nothing references).
        var byValues = new Dictionary<string, string>();
        foreach (var guid in AssetDatabase.FindAssets("t:PlayerSettings", new[] { Folder }))
        {
            string existing = AssetDatabase.GUIDToAssetPath(guid);
            byValues[JsonUtility.ToJson(AssetDatabase.LoadAssetAtPath<PlayerSettings>(existing))] = existing;
        }
        string log = "";

        PlayerSettings For(PlayerMovement movement, string where)
        {
            var probe = ScriptableObject.CreateInstance<PlayerSettings>();
            probe.CopyFrom(movement);
            string key = JsonUtility.ToJson(probe);
            if (byValues.TryGetValue(key, out var found)) { Object.DestroyImmediate(probe); return AssetDatabase.LoadAssetAtPath<PlayerSettings>(found); }
            string name = Names.TryGetValue(where, out var n) ? n : where;
            string path = AssetDatabase.GenerateUniqueAssetPath(Folder + "/Player Settings - " + name + ".asset");
            AssetDatabase.CreateAsset(probe, path);
            byValues[key] = path;
            log += "made " + Path.GetFileNameWithoutExtension(path) + " from " + where + "\n";
            return probe;
        }

        // The prefab first (the Tutorial and any new scene made from it use it).
        var prefab = PrefabUtility.LoadPrefabContents(PrefabPath);
        var prefabMovement = prefab.GetComponent<PlayerMovement>();
        if (prefabMovement != null && prefabMovement.settings == null)
        {
            prefabMovement.settings = For(prefabMovement, "Player.prefab");
            PrefabUtility.SaveAsPrefabAsset(prefab, PrefabPath);
            log += "Player.prefab -> " + prefabMovement.settings.name + "\n";
        }
        PrefabUtility.UnloadPrefabContents(prefab);

        string active = UnityEngine.SceneManagement.SceneManager.GetActiveScene().path;
        foreach (var path in Directory.GetFiles("Assets/Scenes", "*.unity").OrderBy(p => p))
        {
            var scene = EditorSceneManager.OpenScene(path, OpenSceneMode.Single);
            var players = Object.FindObjectsByType<PlayerMovement>(FindObjectsInactive.Include, FindObjectsSortMode.None);
            bool changed = false;
            // Unlinked players, and players whose own values differ from their link (a Player.prefab instance with
            // overrides, like the Tutorial's, inherits the prefab's link but would lose its overrides to it).
            foreach (var movement in players.Where(m => m.settings == null || !Matches(m)))
            {
                // Prefab instances too: with the prefab's values they land on the same asset; with their own, their own one.
                movement.settings = For(movement, Path.GetFileNameWithoutExtension(path));
                EditorUtility.SetDirty(movement);
                log += Path.GetFileNameWithoutExtension(path) + " -> " + movement.settings.name + "\n";
                changed = true;
            }
            if (changed) EditorSceneManager.SaveScene(scene);
        }
        AssetDatabase.SaveAssets();
        if (!string.IsNullOrEmpty(active)) EditorSceneManager.OpenScene(active, OpenSceneMode.Single);
        return log.Length > 0 ? log : "Every Player is already linked.";
    }
}
