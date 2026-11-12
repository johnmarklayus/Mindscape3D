using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

// School_Grounds.glb furnishes only Room 03 (the story's classroom); Rooms 01, 02 and 04 along the same corridor were
// bare shells with a floor that stops halfway, so walking into one showed an empty box. This copies Room 03's
// furniture (its rows of double desks and seats, the teacher's desk and chair, the bookcase, the books) and its full
// floor into the other three rooms, in every scene with the campus. Room 03's own furniture is untouched. Copies are
// named "Furnished | Room 0N | ..." under the campus, so running it again replaces them.
public static class SchoolSpareClassrooms
{
    const string Prefix = "Furnished | ";
    static readonly (string room, float dx)[] Rooms = { ("Room 04", -20), ("Room 02", 20), ("Room 01", 40) };
    static readonly string[] Furniture = { "Double_Desk", "Seat_", "Teacher_Desk", "Detail_Teacher", "Detail_Bookcase", "Floor" };

    [MenuItem("Mindscape/School/Furnish Empty Classrooms in All Scenes")]
    public static void ApplyAllMenu()
    {
        string active = SceneManager.GetActiveScene().path;
        foreach (var path in SchoolModelSync.FindScenes())
        {
            if (path.Contains("/Prototypes/")) continue;
            var scene = EditorSceneManager.OpenScene(path, OpenSceneMode.Single);
            int n = Apply(scene);
            if (n == 0) continue;
            EditorSceneManager.MarkSceneDirty(scene); EditorSceneManager.SaveScene(scene);
            Debug.Log("Classrooms · " + Path.GetFileNameWithoutExtension(path) + ": " + n + " parts");
        }
        if (!string.IsNullOrEmpty(active)) EditorSceneManager.OpenScene(active, OpenSceneMode.Single);
    }

    public static int Apply(Scene scene)
    {
        int made = 0;
        foreach (var campus in SchoolModelSync.FindCampuses(scene))
        {
            var t = campus.transform;
            foreach (var old in t.GetComponentsInChildren<Transform>(true).Where(c => c != null && c.name.StartsWith(Prefix, StringComparison.Ordinal)).ToArray())
                if (old != null) UnityEngine.Object.DestroyImmediate(old.gameObject);
            var source = t.GetComponentsInChildren<Transform>(true)
                .Where(c => c.name.StartsWith("Room 03 | ", StringComparison.Ordinal) && Furniture.Any(f => c.name.Substring(10).StartsWith(f, StringComparison.Ordinal)))
                .ToArray();
            if (source.Length == 0) continue;
            foreach (var (room, dx) in Rooms)
            {
                // A room that already has desks (or was removed from this campus) is left alone.
                var parts = t.GetComponentsInChildren<Transform>(true).Where(c => c.name.StartsWith(room + " | ", StringComparison.Ordinal)).ToArray();
                if (parts.Length == 0 || parts.Any(c => c.name.Contains("Desk"))) continue;
                // Its own half floor gives way to the full copy.
                foreach (var floor in parts.Where(c => c.name == room + " | Floor")) floor.gameObject.SetActive(false);
                Vector3 offset = new Vector3(dx, 0, 0);
                foreach (var part in source)
                {
                    var copy = UnityEngine.Object.Instantiate(part.gameObject, part.parent);
                    copy.name = Prefix + room + " | " + part.name.Substring(10);
                    copy.transform.position = part.position + offset;
                    copy.transform.rotation = part.rotation;
                    copy.SetActive(part.gameObject.activeSelf);
                    made++;
                }
                made += CloseSideWalls(t, room, parts);
            }
        }
        return made;
    }

    // The spare rooms' window walls (Left_Wall_*) stop where their old half floor ended, so the back of the room stood
    // open to the yard (testers saw the desks from outside). A plain wall section closes the gap up to the back wall,
    // using the room's own wall material and with a collider.
    static int CloseSideWalls(Transform campus, string room, Transform[] parts)
    {
        Renderer R(Transform x) => x != null ? x.GetComponent<Renderer>() : null;
        var back = parts.Select(R).FirstOrDefault(r => r != null && r.name == room + " | Back_Wall");
        var solid = parts.Select(R).FirstOrDefault(r => r != null && r.name == room + " | Right_Wall");
        if (back == null || solid == null) return 0;
        int made = 0;
        foreach (var side in new[] { "Left_Wall", "Right_Wall" })
        {
            var pieces = parts.Select(R).Where(r => r != null && r.name.StartsWith(room + " | " + side, StringComparison.Ordinal)).ToArray();
            if (pieces.Length == 0) continue;
            var b = pieces[0].bounds; foreach (var r in pieces) b.Encapsulate(r.bounds);
            var wall = back.bounds;
            // The back wall runs along X; the side walls along Z. Whichever end of the side wall is nearer the back wall.
            bool backIsLow = Mathf.Abs(wall.center.z - b.min.z) < Mathf.Abs(wall.center.z - b.max.z);
            float from = backIsLow ? wall.center.z : b.max.z, to = backIsLow ? b.min.z : wall.center.z;
            if (to - from < .3f) continue;
            var fill = GameObject.CreatePrimitive(PrimitiveType.Cube);
            fill.name = Prefix + room + " | " + side + "_Fill";
            fill.transform.position = new Vector3(b.center.x, (wall.min.y + wall.max.y) * .5f, (from + to) * .5f);
            fill.transform.localScale = new Vector3(b.size.x, wall.size.y, to - from + b.size.x);
            fill.transform.SetParent(campus, true);
            fill.GetComponent<Renderer>().sharedMaterial = solid.sharedMaterial;
            fill.isStatic = solid.gameObject.isStatic;
            fill.layer = solid.gameObject.layer;
            made++;
        }
        return made;
    }
}
