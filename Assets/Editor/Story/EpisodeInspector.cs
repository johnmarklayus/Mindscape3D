using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using Mindscape.AcademicPressure;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

/// <summary>
/// The Inspector of every story episode (any AcademicEpisode): the usual fields, then
///   Scene points  every spot, start point and camera view the episode uses (Transforms in the scene): select one to
///                 move it in the Scene view;
///   Story markers the positions the code works out that a StoryMarker can take over, whether the scene has one, and
///                 a button that creates the missing markers at their built-in positions.
/// The points are also drawn in the Scene view (labels when the episode is selected).
/// </summary>
[CustomEditor(typeof(AcademicEpisode), true)]
public class EpisodeInspector : Editor
{
    bool showPoints = true, showMarkers = true;
    List<StoryMarkerDefault> defaults;
    string error;

    public override void OnInspectorGUI()
    {
        DrawDefaultInspector();
        var episode = (AcademicEpisode)target;

        EditorGUILayout.Space(10);
        showPoints = EditorGUILayout.BeginFoldoutHeaderGroup(showPoints, "Scene points (drag them in the Scene view)");
        if (showPoints)
        {
            var points = ScenePoints(episode).ToList();
            if (points.Count == 0) EditorGUILayout.HelpBox("This episode has no Transform fields.", MessageType.None);
            foreach (var (label, t) in points)
            {
                using (new EditorGUILayout.HorizontalScope())
                {
                    EditorGUILayout.LabelField(label, t != null ? t.name : "(not set)");
                    using (new EditorGUI.DisabledScope(t == null))
                        if (GUILayout.Button("Select", GUILayout.Width(60))) { Selection.activeTransform = t; SceneView.lastActiveSceneView?.FrameSelected(); }
                }
            }
        }
        EditorGUILayout.EndFoldoutHeaderGroup();

        EditorGUILayout.Space(6);
        showMarkers = EditorGUILayout.BeginFoldoutHeaderGroup(showMarkers, "Story markers (positions you can move without code)");
        if (showMarkers)
        {
            // Listed once per selection: some built-in positions take a moment to work out (the sofa seat scan).
            if (defaults == null)
            {
                try { Physics.SyncTransforms(); defaults = episode.MarkerDefaults().ToList(); error = null; }
                catch (System.Exception e) { defaults = new List<StoryMarkerDefault>(); error = e.Message; }
            }
            if (error != null) EditorGUILayout.HelpBox("Could not list the markers: " + error, MessageType.Warning);
            if (defaults.Count == 0)
                EditorGUILayout.HelpBox("This episode has no positions worked out in code: everything it uses is in the Scene points above.", MessageType.None);
            else
            {
                EditorGUILayout.HelpBox("Each marker below takes over a position the code works out. Without a marker in the scene the built-in position is used. Create the markers, then drag them (the blue arrow is the way a person faces or a camera looks).", MessageType.Info);
                foreach (var d in defaults)
                {
                    var marker = StoryMarker.Find(d.id);
                    using (new EditorGUILayout.HorizontalScope())
                    {
                        EditorGUILayout.LabelField(new GUIContent(d.id, d.note), new GUIContent(marker != null ? "in scene" : "built-in", d.note));
                        if (marker != null && GUILayout.Button("Select", GUILayout.Width(60))) { Selection.activeObject = marker.gameObject; SceneView.lastActiveSceneView?.FrameSelected(); }
                    }
                }
                using (new EditorGUI.DisabledScope(defaults.All(d => StoryMarker.Find(d.id) != null)))
                    if (GUILayout.Button("Create missing markers at their built-in positions"))
                        Debug.Log("[Story markers] " + StoryMarkerTools.CreateMissing(episode) + " created.");
            }
        }
        EditorGUILayout.EndFoldoutHeaderGroup();
    }

    /// <summary>Every Transform (and Transform array entry) the episode is wired to, except the player and the camera.</summary>
    public static IEnumerable<(string label, Transform t)> ScenePoints(AcademicEpisode episode)
    {
        for (var type = episode.GetType(); type != null && type != typeof(MonoBehaviour); type = type.BaseType)
            foreach (var f in type.GetFields(BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.DeclaredOnly))
            {
                if (f.Name == nameof(AcademicEpisode.player)) continue;
                if (!f.IsPublic && f.GetCustomAttribute<SerializeField>() == null) continue;
                string name = ObjectNames.NicifyVariableName(f.Name);
                if (f.FieldType == typeof(Transform)) yield return (name, (Transform)f.GetValue(episode));
                else if (f.FieldType == typeof(Transform[]) && f.GetValue(episode) is Transform[] array)
                    for (int i = 0; i < array.Length; i++) yield return (name + " " + i, array[i]);
            }
    }

    [DrawGizmo(GizmoType.Selected | GizmoType.NonSelected)]
    static void DrawPoints(AcademicEpisode episode, GizmoType type)
    {
        bool selected = (type & GizmoType.Selected) != 0 || Selection.transforms.Any(t => t.IsChildOf(episode.transform));
        foreach (var (label, t) in ScenePoints(episode))
        {
            if (t == null) continue;
            bool view = label.ToLowerInvariant().Contains("view") || label.ToLowerInvariant().Contains("shot") || label.ToLowerInvariant().Contains("camera");
            Gizmos.color = view ? new Color(.35f, .7f, 1f, selected ? 1 : .35f) : new Color(1f, .85f, .3f, selected ? 1 : .35f);
            if (view)
            {
                Gizmos.matrix = Matrix4x4.TRS(t.position, t.rotation, Vector3.one);
                Gizmos.DrawFrustum(Vector3.zero, 50, 1f, .1f, 16f / 9f);
                Gizmos.matrix = Matrix4x4.identity;
            }
            else
            {
                Gizmos.DrawWireSphere(t.position, .3f);
                Gizmos.DrawLine(t.position, t.position + t.forward * .7f);
            }
            if (selected) { Handles.color = Gizmos.color; Handles.Label(t.position + Vector3.up * .6f, label); }
        }
    }
}

/// <summary>Creating Story Markers: from an episode's Inspector, or for every episode scene at once.</summary>
public static class StoryMarkerTools
{
    const string GroupName = "Story Markers";

    /// <summary>Adds a marker for every id the episode reads that the scene does not have yet. Returns how many.</summary>
    public static int CreateMissing(AcademicEpisode episode)
    {
        Physics.SyncTransforms();
        int made = 0;
        Transform group = null;
        foreach (var d in episode.MarkerDefaults().ToList())
        {
            if (StoryMarker.Find(d.id) != null) continue;
            if (group == null)
            {
                group = episode.transform.Find(GroupName);
                if (group == null)
                {
                    group = new GameObject(GroupName).transform;
                    Undo.RegisterCreatedObjectUndo(group.gameObject, "Create story markers");
                    group.SetParent(episode.transform, false);
                }
            }
            var go = new GameObject(d.id.Replace('/', ' '));
            Undo.RegisterCreatedObjectUndo(go, "Create story markers");
            go.transform.SetParent(group, false);
            go.transform.SetPositionAndRotation(d.position, d.rotation);
            var marker = go.AddComponent<StoryMarker>();
            marker.id = d.id; marker.kind = d.kind; marker.note = d.note;
            made++;
        }
        if (made > 0) EditorSceneManager.MarkSceneDirty(episode.gameObject.scene);
        return made;
    }

    [MenuItem("Mindscape/Story/Create Missing Story Markers (All Episode Scenes)", priority = 20)]
    static void Menu() => Debug.Log(CreateMissingInAllScenes());

    /// <summary>Opens every scene in Assets/Scenes, adds the missing markers and saves the scenes that changed.</summary>
    public static string CreateMissingInAllScenes()
    {
        if (!Application.isBatchMode && !EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo()) return "Cancelled.";
        string active = SceneManager.GetActiveScene().path, log = "";
        foreach (var path in System.IO.Directory.GetFiles("Assets/Scenes", "*.unity"))
        {
            var scene = EditorSceneManager.OpenScene(path, OpenSceneMode.Single);
            var episode = Object.FindFirstObjectByType<AcademicEpisode>(FindObjectsInactive.Include);
            if (episode == null) continue;
            int made = CreateMissing(episode);
            if (made == 0) continue;
            EditorSceneManager.SaveScene(scene);
            log += System.IO.Path.GetFileNameWithoutExtension(path) + ": " + made + " markers\n";
        }
        if (!string.IsNullOrEmpty(active)) EditorSceneManager.OpenScene(active, OpenSceneMode.Single);
        return log.Length > 0 ? log : "Every episode scene already has its markers.";
    }
}
