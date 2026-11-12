using System.IO;
using System.Linq;
using Mindscape;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

// Puts Joey's bed model (Assets/Models/Bed/Joey Bed.fbx, from Blender/Blend Files/Boy_Sleeping_In_Bed.blend) in place of
// the house model's own bed in every scene with the house: same spot, same length, head by the bedside table. The house's
// bed parts are switched off and every story reference to them moves to the new bed's states (messy -> Messy,
// fixed -> Neat), so the episodes' "Make your bed" and BedModeController keep working. Runs after every episode builder
// (WorldModelSync.Apply) and from Mindscape > House > Install Joey Bed. Running it again is safe.
public static class BedInstaller
{
    public const string ModelPath = "Assets/Models/Bed/Joey Bed.fbx";
    const string InstanceName = "Joey Bed";
    const string Bed = "West bedroom | bed", BedFixed = "West bedroom | bed fixed", BedMessy = "West bedroom | bed messy",
        UnmadeBed = "West bedroom | unmade bed", Table = "West bedroom | bedside table";

    [MenuItem("Mindscape/House/Install Joey Bed (all scenes)")]
    static void Menu() => Debug.Log(ApplyAll());

    public static string ApplyAll()
    {
        string active = SceneManager.GetActiveScene().path, log = "";
        foreach (var path in Directory.GetFiles("Assets/Scenes", "*.unity"))
        {
            var scene = EditorSceneManager.OpenScene(path, OpenSceneMode.Single);
            string result = Apply(scene);
            if (result == null) continue;
            EditorSceneManager.MarkSceneDirty(scene); EditorSceneManager.SaveScene(scene);
            log += "Joey bed · " + Path.GetFileNameWithoutExtension(path) + ": " + result + "\n";
        }
        if (!string.IsNullOrEmpty(active)) EditorSceneManager.OpenScene(active, OpenSceneMode.Single);
        return log;
    }

    // Null when the scene has no house bed.
    public static string Apply(Scene scene)
    {
        Transform house = null;
        foreach (var root in scene.GetRootGameObjects())
        {
            var t = root.name == "House And Lot" ? root.transform : FindDeep(root.transform, "House And Lot");
            if (t != null && FindDeep(t, Bed) != null) { house = t; break; }
        }
        if (house == null) return null;
        var model = AssetDatabase.LoadAssetAtPath<GameObject>(ModelPath);
        if (model == null) return "no " + ModelPath + ", skipped";

        var bed = FindDeep(house, Bed); var fixedBed = FindDeep(house, BedFixed);
        var messyBed = FindDeep(house, BedMessy); var unmade = FindDeep(house, UnmadeBed); var table = FindDeep(house, Table);
        var old = new[] { bed, fixedBed, messyBed, unmade }.Where(t => t != null).ToArray();

        // Which look the scene had: an active house part says so (a builder may just have switched it on); otherwise
        // the installed bed keeps what it shows.
        var states = scene.GetRootGameObjects().Select(g => g.GetComponentInChildren<BedStates>(true)).FirstOrDefault(s => s != null);
        bool anyOld = old.Any(t => t.gameObject.activeSelf && t != bed);
        bool messy = anyOld ? (messyBed != null && messyBed.gameObject.activeSelf) || (unmade != null && unmade.gameObject.activeSelf)
            : states != null && states.messy != null && states.messy.activeSelf;

        // Footprint of the old bed (frame + bedding), from the meshes so it also works once they are switched off.
        Bounds area = WorldBounds(bed);
        if (fixedBed != null) area.Encapsulate(WorldBounds(fixedBed));
        bool alongX = area.size.x >= area.size.z;
        Vector3 head = alongX ? Vector3.right : Vector3.forward;
        if (table != null && Vector3.Dot(WorldBounds(table).center - area.center, head) < 0) head = -head;

        if (states == null)
        {
            var go = (GameObject)PrefabUtility.InstantiatePrefab(model, scene);
            go.name = InstanceName;
            states = go.AddComponent<BedStates>();
        }
        var tr = states.transform;
        Transform Part(string name) => FindDeep(tr, name);
        states.sleepingBoy = Part("Sleeping boy")?.gameObject; states.sleepingGirl = Part("Sleeping girl")?.gameObject;
        states.messy = Part("Messy")?.gameObject; states.neat = Part("Neat")?.gameObject;
        states.mattress = Part("Bed frame | Bed_Mattress")?.GetComponent<Renderer>();
        states.frame = Part("Bed frame | Bed_Frame")?.GetComponent<Renderer>();
        if (states.mattress == null || states.frame == null || states.messy == null || states.neat == null)
            return "the bed model is missing parts, skipped";

        // The model's own length and head direction, measured as imported (its root keeps the FBX axis rotation and
        // scale; the turn and the size are added on top of them).
        Quaternion baseRotation = model.transform.localRotation; Vector3 baseScale = model.transform.localScale;
        tr.SetPositionAndRotation(Vector3.zero, baseRotation); tr.localScale = baseScale;
        Bounds frameBox = WorldBounds(states.frame.transform);
        var board = Part("Bed frame | Bed_Headboard");
        Vector3 modelHead = board != null ? WorldBounds(board).center - frameBox.center : Vector3.back;
        modelHead.y = 0;
        modelHead = Mathf.Abs(modelHead.x) > Mathf.Abs(modelHead.z) ? new Vector3(Mathf.Sign(modelHead.x), 0, 0) : new Vector3(0, 0, Mathf.Sign(modelHead.z));
        float modelLength = Mathf.Abs(Vector3.Dot(frameBox.size, modelHead));
        float oldLength = Mathf.Abs(Vector3.Dot(area.size, head));
        float scale = oldLength / Mathf.Max(.01f, modelLength);

        Quaternion turn = Quaternion.FromToRotation(modelHead, head);
        if (Mathf.Abs(Vector3.Dot(modelHead, head) + 1) < 1e-3) turn = Quaternion.Euler(0, 180, 0);   // keep it upright
        tr.localScale = baseScale * scale;
        tr.rotation = turn * baseRotation;
        // The model's origin is the middle of the bed on the floor.
        Vector3 centreOffset = turn * (new Vector3(frameBox.center.x, 0, frameBox.center.z) * scale);
        tr.position = new Vector3(area.center.x, area.min.y, area.center.z) - centreOffset;

        // Something solid to bump into and to lie on (the story raycasts down onto the mattress).
        foreach (var name in new[] { "Bed frame | Bed_Mattress", "Bed frame | Bed_Frame", "Bed frame | Bed_Headboard", "Bed frame | Bed_Footboard" })
        {
            var part = Part(name);
            if (part != null && part.GetComponent<Collider>() == null) part.gameObject.AddComponent<BoxCollider>();
        }

        if (states.sleepingBoy != null) states.sleepingBoy.SetActive(false);
        if (states.sleepingGirl != null) states.sleepingGirl.SetActive(false);
        states.messy.SetActive(messy);
        states.neat.SetActive(!messy);

        // Story references to the old bed parts move to the new states; the old parts go dark.
        int rewired = 0;
        foreach (var t in new[] { messyBed, unmade }.Where(t => t != null))
            rewired += Rewire(scene, t.gameObject, states.messy) + Rewire(scene, t, states.messy.transform);
        if (fixedBed != null) rewired += Rewire(scene, fixedBed.gameObject, states.neat) + Rewire(scene, fixedBed, states.neat.transform);
        foreach (var t in old) t.gameObject.SetActive(false);

        // A story that switches the messy bed off ("Make your bed") must switch the neat one on: fill an empty fixedBed.
        foreach (var behaviour in scene.GetRootGameObjects().SelectMany(g => g.GetComponentsInChildren<MonoBehaviour>(true)))
        {
            if (behaviour == null) continue;
            var so = new SerializedObject(behaviour);
            var m = so.FindProperty("messyBed"); var f = so.FindProperty("fixedBed");
            if (m == null || f == null || m.objectReferenceValue != states.messy || f.objectReferenceValue != null) continue;
            f.objectReferenceValue = states.neat; so.ApplyModifiedPropertiesWithoutUndo(); rewired++;
        }

        EditorSceneManager.MarkSceneDirty(scene);
        return (messy ? "messy" : "neat") + ", scale " + scale.ToString("0.00") + ", " + rewired + " reference(s) moved";
    }

    static Bounds WorldBounds(Transform t)
    {
        bool any = false; var b = new Bounds();
        foreach (var f in t.GetComponentsInChildren<MeshFilter>(true))
        {
            if (f.sharedMesh == null) continue;
            var mb = f.sharedMesh.bounds; var m = f.transform.localToWorldMatrix;
            for (int i = 0; i < 8; i++)
            {
                var corner = m.MultiplyPoint3x4(mb.center + Vector3.Scale(mb.extents, new Vector3((i & 1) == 0 ? -1 : 1, (i & 2) == 0 ? -1 : 1, (i & 4) == 0 ? -1 : 1)));
                if (!any) { b = new Bounds(corner, Vector3.zero); any = true; } else b.Encapsulate(corner);
            }
        }
        return any ? b : new Bounds(t.position, Vector3.zero);
    }

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
