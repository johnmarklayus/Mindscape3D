using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

// The house's two rooms off the hallway: the bathroom behind Door_Bathroom (where Joey changes into his uniform) and
// the second bedroom behind Door_Bedroom_Right. Their furniture is part of the house model now
// (Blender/Blend Files/house-and-lot-cozy.blend, collection "INTERIOR | Bathroom and spare room"; parts named "Bathroom | ..."
// and "Spare room | ..."), so every scene linked to Assets/house-and-lot-cozy.fbx gets it with the model. The FBX's
// materials are remapped to Assets/Models/House Rooms.
//
// This used to build the rooms out of Unity cubes and cylinders in each scene. Now it only tidies a scene: it removes
// those old scene-built pieces, adds any model part an unlinked house is missing, and gives the solid pieces
// colliders (the FBX imports without them). WorldModelSync.Apply calls it, so the episode builders keep the rooms.
public static class HouseSpareRooms
{
    const string BathroomPrefix = "Bathroom | ", BedroomPrefix = "Spare room | ";

    // Parts you bump into; the rest (tiles, trim, small items) stay walk-through like before.
    static readonly string[] Solid =
    {
        BathroomPrefix + "shower tray", BathroomPrefix + "shower glass side", BathroomPrefix + "shower glass front",
        BathroomPrefix + "toilet base", BathroomPrefix + "toilet tank", BathroomPrefix + "vanity cabinet",
        BedroomPrefix + "desk top", BedroomPrefix + "desk leg", BedroomPrefix + "chair seat",
        BedroomPrefix + "bed fixed", BedroomPrefix + "bed", BedroomPrefix + "bedside table", BedroomPrefix + "bedside lamp",
        BedroomPrefix + "wall poster 1", BedroomPrefix + "wall poster 2", BedroomPrefix + "woven bedside rug", BedroomPrefix + "wardrobe",
        StudyDesk, StudyChair,
    };

    // Joey's bedroom props and the dinner plates are model parts too (collection "INTERIOR | Bedroom and dining props").
    // The episode builders still make their old cube versions under the story root; Props() swaps them for the model's.
    const string StudyDesk = "West bedroom | study desk", StudyChair = "West bedroom | study chair";
    const string UnmadeBed = "West bedroom | unmade bed", DinnerPlates = "Dining | dinner plates";
    static readonly string[] ModelledProps = { "Study desk", "Desk leg", "Study chair", "Desk lamp base", "Dinner plate", "Rice bowl" };
    // The story that sets the dinner table (Ch2 Ep5; Ch3 Ep1/7/8 keep a copy of its root).
    const string DinnerStory = "Chapter 2 · Episode 5 - What I Left Behind";

    [MenuItem("Mindscape/House/Furnish Spare Rooms (open scene)")]
    static void ApplyOpenMenu()
    {
        var scene = SceneManager.GetActiveScene();
        Debug.Log("Spare rooms: " + Apply(scene));
        EditorSceneManager.MarkSceneDirty(scene);
    }

    [MenuItem("Mindscape/House/Furnish Spare Rooms (all house scenes)")]
    static void ApplyAllMenu()
    {
        if (!EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo()) return;
        Debug.Log(ApplyAll());
    }

    /// <summary>Runs Apply on every scene with the house and saves it. Returns one line per scene.</summary>
    public static string ApplyAll()
    {
        string active = SceneManager.GetActiveScene().path, log = "";
        foreach (var path in Directory.GetFiles("Assets/Scenes", "*.unity"))
        {
            var scene = EditorSceneManager.OpenScene(path, OpenSceneMode.Single);
            string result = Apply(scene);
            if (result == null) continue;
            EditorSceneManager.MarkSceneDirty(scene); EditorSceneManager.SaveScene(scene);
            log += "Spare rooms · " + Path.GetFileNameWithoutExtension(path) + ": " + result + "\n";
        }
        if (!string.IsNullOrEmpty(active)) EditorSceneManager.OpenScene(active, OpenSceneMode.Single);
        return log;
    }

    // Null when the scene has no house with these rooms.
    public static string Apply(Scene scene)
    {
        Transform house = null;
        foreach (var root in scene.GetRootGameObjects())
        {
            var t = root.name == "House And Lot" ? root.transform : FindDeep(root.transform, "House And Lot");
            if (t != null && FindDeep(t, "Door_Bathroom") != null) { house = t; break; }
        }
        if (house == null) return null;

        // The old scene-built pieces: anything with these names that does not come from the model.
        int removed = 0;
        foreach (var child in house.Cast<Transform>().Where(IsRoomPart).ToArray())
            if (PrefabUtility.GetCorrespondingObjectFromSource(child.gameObject) == null) { Object.DestroyImmediate(child.gameObject); removed++; }

        // A house no longer linked to the model does not get new model parts by itself.
        int added = 0;
        var model = AssetDatabase.LoadAssetAtPath<GameObject>(HouseModelSync.ModelPath);
        foreach (var part in model.transform.Cast<Transform>().Where(IsRoomPart))
        {
            if (house.Find(part.name) != null) continue;
            var copy = Object.Instantiate(part.gameObject, house, false);
            copy.name = part.name;
            copy.transform.SetLocalPositionAndRotation(part.localPosition, part.localRotation);
            copy.transform.localScale = part.localScale;
            added++;
        }

        string props = Props(scene, house);

        int colliders = 0;
        foreach (var part in house.Cast<Transform>().Where(t => IsRoomPart(t) || Solid.Contains(t.name)))
        {
            part.gameObject.isStatic = true;
            var meshFilter = part.GetComponent<MeshFilter>();
            if (!Solid.Contains(part.name) || meshFilter == null || part.GetComponent<Collider>() != null) continue;
            part.gameObject.AddComponent<MeshCollider>().sharedMesh = meshFilter.sharedMesh;
            colliders++;
        }
        return removed + " old scene-built piece(s) removed, " + added + " model part(s) added, " + colliders + " collider(s) added; " + props;
    }

    // The story's cube-built desk, legs, chair, lamp, plates and bowls go (the model has them). The unmade bed is a
    // story switch (messyBed): references move to the model's bed, which takes over its on/off state. The alarm clock
    // keeps its story object (its position, collider and digits) but loses its own boxes. The model's dinner plates
    // show only where the dinner story is.
    static string Props(Scene scene, Transform house)
    {
        var outside = scene.GetRootGameObjects().Where(g => g.transform != house)
            .SelectMany(g => g.GetComponentsInChildren<Transform>(true)).Where(t => !t.IsChildOf(house)).ToArray();
        bool dinner = outside.Any(t => t.name == "Dinner plate" || t.name == "Rice bowl" || t.name == DinnerStory);

        int removed = 0;
        foreach (var t in outside.Where(t => ModelledProps.Contains(t.name) && t.GetComponentsInChildren<MeshFilter>(true).Length > 0).ToArray())
            if (t != null) { Object.DestroyImmediate(t.gameObject); removed++; }
        outside = outside.Where(t => t != null).ToArray();

        int rewired = 0;
        var modelBed = house.Find(UnmadeBed);
        foreach (var bed in outside.Where(t => t != null && t.name == "Unmade bed").ToArray())
        {
            if (modelBed == null) break;
            rewired += Rewire(scene, bed.gameObject, modelBed.gameObject) + Rewire(scene, bed, modelBed);
            modelBed.gameObject.SetActive(bed.gameObject.activeSelf);
            Object.DestroyImmediate(bed.gameObject); removed++;
        }

        foreach (var clock in outside.Where(t => t != null && t.name == "Bedside alarm clock").ToArray())
        {
            var face = clock.Find("Clock face"); if (face != null) { Object.DestroyImmediate(face.gameObject); removed++; }
            var renderer = clock.GetComponent<MeshRenderer>(); if (renderer != null) Object.DestroyImmediate(renderer);
            var filter = clock.GetComponent<MeshFilter>(); if (filter != null) Object.DestroyImmediate(filter);
        }

        var plates = house.Find(DinnerPlates);
        if (plates != null) plates.gameObject.SetActive(dinner);
        return removed + " cube prop(s) removed, " + rewired + " reference(s) moved to the model bed, dinner plates " + (dinner ? "on" : "off");
    }

    // Points every serialized reference to `from` (in this scene's scripts) at `to`.
    static int Rewire(Scene scene, Object from, Object to)
    {
        int n = 0;
        foreach (var behaviour in scene.GetRootGameObjects().SelectMany(g => g.GetComponentsInChildren<MonoBehaviour>(true)))
        {
            if (behaviour == null) continue;
            var so = new SerializedObject(behaviour); var it = so.GetIterator(); bool changed = false;
            while (it.Next(true))
                if (it.propertyType == SerializedPropertyType.ObjectReference && it.objectReferenceValue == from) { it.objectReferenceValue = to; changed = true; n++; }
            if (changed) so.ApplyModifiedPropertiesWithoutUndo();
        }
        return n;
    }

    static bool IsRoomPart(Transform t) => t.name.StartsWith(BathroomPrefix) || t.name.StartsWith(BedroomPrefix);

    static Transform FindDeep(Transform parent, string name)
    {
        foreach (Transform child in parent)
        {
            if (child.name == name) return child;
            var found = FindDeep(child, name);
            if (found != null) return found;
        }
        return null;
    }
}
