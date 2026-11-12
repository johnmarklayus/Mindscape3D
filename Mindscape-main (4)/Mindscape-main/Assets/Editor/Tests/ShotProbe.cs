using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

// Batch-mode helper for checking scenes without the editor UI: renders views to PNG and lists object positions.
//   Unity -batchmode -projectPath . -executeMethod ShotProbe.Run -probeFile <commands.txt> -probeOut <folder> -quit
// Commands, one per line (# comments):
//   open <scene path>
//   shot <name> px py pz lx ly lz [fov] [width height]   render from p looking at l into <out>/<name>.png
//   top <name> cx cz size [height]                       orthographic top-down view centred at (cx, cz)
//   find <text>                                          log every object whose name contains text (position, bounds)
//   tree <object name> [depth]                           log an object's children with positions
//   ray px py pz dx dy dz                                log what a ray hits
//   method <Type.Method>                                 call a static method (for builders)
//   save                                                 save open scenes
public static class ShotProbe
{
    static readonly StringBuilder log = new StringBuilder();
    static string outDir;

    public static void Run()
    {
        var args = System.Environment.GetCommandLineArgs();
        string Arg(string key) { int i = System.Array.IndexOf(args, key); return i >= 0 && i + 1 < args.Length ? args[i + 1] : null; }
        string file = Arg("-probeFile");
        outDir = Arg("-probeOut") ?? Path.GetDirectoryName(file);
        Directory.CreateDirectory(outDir);
        foreach (var raw in File.ReadAllLines(file))
        {
            var line = raw.Trim();
            if (line.Length == 0 || line.StartsWith("#")) continue;
            try { Do(line); }
            catch (System.Exception e) { Log("ERROR " + line + " : " + e); }
        }
        File.WriteAllText(Path.Combine(outDir, "probe-log.txt"), log.ToString());
    }

    static void Log(string s) { log.AppendLine(s); Debug.Log("[probe] " + s); }
    static float F(string s) => float.Parse(s, CultureInfo.InvariantCulture);
    static string V(Vector3 v) => v.x.ToString("0.00", CultureInfo.InvariantCulture) + "," + v.y.ToString("0.00", CultureInfo.InvariantCulture) + "," + v.z.ToString("0.00", CultureInfo.InvariantCulture);

    static void Do(string line)
    {
        var parts = line.Split(' ');
        string cmd = parts[0];
        if (cmd == "open")
        {
            EditorSceneManager.OpenScene(line.Substring(5).Trim(), OpenSceneMode.Single);
            Log("opened " + line.Substring(5));
        }
        else if (cmd == "shot")
        {
            var p = new Vector3(F(parts[2]), F(parts[3]), F(parts[4]));
            var l = new Vector3(F(parts[5]), F(parts[6]), F(parts[7]));
            float fov = parts.Length > 8 ? F(parts[8]) : 55;
            int w = parts.Length > 10 ? int.Parse(parts[9]) : 960, h = parts.Length > 10 ? int.Parse(parts[10]) : 540;
            Render(parts[1], cam => { cam.transform.position = p; cam.transform.LookAt(l); cam.fieldOfView = fov; }, w, h);
        }
        else if (cmd == "top")
        {
            float cx = F(parts[2]), cz = F(parts[3]), size = F(parts[4]), height = parts.Length > 5 ? F(parts[5]) : 60;
            Render(parts[1], cam =>
            {
                cam.orthographic = true; cam.orthographicSize = size * .5f;
                cam.transform.position = new Vector3(cx, height, cz); cam.transform.rotation = Quaternion.Euler(90, 0, 0);
                cam.nearClipPlane = .1f; cam.farClipPlane = height + 50;
            }, 900, 900);
        }
        else if (cmd == "find")
        {
            string text = line.Substring(5).Trim();
            foreach (var t in AllTransforms().Where(t => t.name.Contains(text)).Take(80))
                Log("find " + PathOf(t) + " active=" + t.gameObject.activeInHierarchy + " pos=" + V(t.position) + " rotY=" + t.eulerAngles.y.ToString("0") + Bounds(t));
        }
        else if (cmd == "tree")
        {
            int depth = parts.Length > 2 && int.TryParse(parts[parts.Length - 1], out var d) ? d : 1;
            string name = parts.Length > 2 && int.TryParse(parts[parts.Length - 1], out _) ? string.Join(" ", parts.Skip(1).Take(parts.Length - 2)) : string.Join(" ", parts.Skip(1));
            var root = AllTransforms().FirstOrDefault(t => t.name == name) ?? AllTransforms().FirstOrDefault(t => PathOf(t).EndsWith(name));
            if (root == null) { Log("tree: no " + name); return; }
            Tree(root, depth, 0);
        }
        else if (cmd == "ray")
        {
            var o = new Vector3(F(parts[1]), F(parts[2]), F(parts[3]));
            var dir = new Vector3(F(parts[4]), F(parts[5]), F(parts[6]));
            Physics.SyncTransforms();
            var hits = Physics.RaycastAll(o, dir.normalized, dir.magnitude, ~0, QueryTriggerInteraction.Ignore).OrderBy(h => h.distance);
            Log("ray " + V(o) + " -> " + V(dir) + ": " + string.Join(" | ", hits.Select(h => PathOf(h.transform) + " @" + V(h.point) + " d=" + h.distance.ToString("0.00"))));
        }
        else if (cmd == "method")
        {
            var name = parts[1]; int dot = name.LastIndexOf('.');
            var type = System.AppDomain.CurrentDomain.GetAssemblies().Select(a => a.GetType(name.Substring(0, dot))).FirstOrDefault(t => t != null);
            var m = type?.GetMethod(name.Substring(dot + 1), System.Reflection.BindingFlags.Static | System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.NonPublic);
            if (m == null) { Log("method not found " + name); return; }
            m.Invoke(null, null);
            Log("ran " + name);
        }
        else if (cmd == "comp")
        {
            string name = line.Substring(5).Trim();
            var go = AllTransforms().FirstOrDefault(t => t.name == name);
            if (go == null) { Log("comp: no " + name); return; }
            foreach (var c in go.GetComponents<MonoBehaviour>())
            {
                if (c == null) continue;
                var so = new SerializedObject(c); var it = so.GetIterator(); bool enter = true;
                var sb = new StringBuilder(c.GetType().Name + ":");
                while (it.NextVisible(enter))
                {
                    enter = it.propertyType == SerializedPropertyType.Generic && it.isArray && it.depth < 1;
                    if (it.propertyType == SerializedPropertyType.ObjectReference && it.objectReferenceValue != null)
                    {
                        var o = it.objectReferenceValue; var tr = o is Component cc ? cc.transform : o is GameObject g ? g.transform : null;
                        sb.Append(" " + it.propertyPath + "=" + o.name + (tr != null ? "@" + V(tr.position) : ""));
                    }
                    else if (it.propertyType == SerializedPropertyType.Float || it.propertyType == SerializedPropertyType.Integer || it.propertyType == SerializedPropertyType.String || it.propertyType == SerializedPropertyType.Boolean)
                        sb.Append(" " + it.propertyPath + "=" + (it.propertyType == SerializedPropertyType.Float ? it.floatValue.ToString("0.##") : it.propertyType == SerializedPropertyType.Integer ? it.intValue.ToString() : it.propertyType == SerializedPropertyType.Boolean ? it.boolValue.ToString() : it.stringValue));
                }
                Log(sb.ToString());
            }
        }
        else if (cmd == "roots")
        {
            foreach (var g in UnityEngine.SceneManagement.SceneManager.GetActiveScene().GetRootGameObjects()) Log("root " + g.name + " active=" + g.activeSelf + " pos=" + V(g.transform.position));
        }
        else if (cmd == "window")
        {
            var t = Mindscape.SocialDynamics.SocialStaging.LoungeWindow(null, new Vector3(F(parts[1]), F(parts[2]), F(parts[3])));
            Log("window " + (t != null ? V(t.position) + " scale " + Bounds(t) : "none"));
        }
        else if (cmd == "park")
        {
            var park = Mindscape.SocialDynamics.SocialStaging.Park(new Vector3(F(parts[1]), F(parts[2]), F(parts[3])));
            Log("park joey=" + V(park.joey) + " justin=" + V(park.justinTo));
        }
        else if (cmd == "place")
        {
            // place <object name> x y z yaw
            var t = AllTransforms().FirstOrDefault(x => x.name == parts[1]);
            if (t != null) t.SetPositionAndRotation(new Vector3(F(parts[2]), F(parts[3]), F(parts[4])), Quaternion.Euler(0, F(parts[5]), 0));
            Physics.SyncTransforms();
            Log("placed " + parts[1] + (t == null ? " (missing)" : ""));
        }
        else if (cmd == "pose")
        {
            // pose <object name> <clip name part> <time>
            var t = AllTransforms().FirstOrDefault(x => x.name == parts[1]);
            var animator = t != null ? t.GetComponentInChildren<Animator>() : null;
            var clip = animator != null && animator.runtimeAnimatorController != null ? animator.runtimeAnimatorController.animationClips.FirstOrDefault(c => c.name.Contains(parts[2])) : null;
            if (clip != null) clip.SampleAnimation(animator.gameObject, F(parts[3]));
            Log("pose " + parts[1] + " " + (clip != null ? clip.name : "no clip"));
        }
        else if (cmd == "girltest")
        {
            // Swap the player to the girl without keeping the choice (the editor's prefs are restored).
            string key = Mindscape.Data.MindscapeDatabase.ProfileKey("Mindscape.Character");
            bool had = PlayerPrefs.HasKey(key); string was = PlayerPrefs.GetString(key, "");
            try { PlayerAppearance.Choose(true); PlayerAppearance.Apply(Object.FindAnyObjectByType<PlayerMovement>().transform); }
            finally { if (had) PlayerPrefs.SetString(key, was); else PlayerPrefs.DeleteKey(key); PlayerPrefs.Save(); }
            Log("girl applied");
        }
        else if (cmd == "backpack")
        {
            var player = Object.FindAnyObjectByType<PlayerMovement>();
            Mindscape.AcademicPressure.PlayerOutfit.Wear(player, Mindscape.AcademicPressure.Outfit.SchoolUniform);
            Mindscape.AcademicPressure.PlayerBackpack.Wear(player.transform, true);
            Log("backpack on " + V(player.transform.position));
        }
        else if (cmd == "asset")
        {
            // asset <path> x y z : instantiate a model and list its materials
            var a = AssetDatabase.LoadAssetAtPath<GameObject>(parts[1]);
            if (a == null) { Log("asset missing " + parts[1]); return; }
            var go = (GameObject)PrefabUtility.InstantiatePrefab(a);
            go.transform.position = new Vector3(F(parts[2]), F(parts[3]), F(parts[4]));
            go.transform.rotation = Quaternion.Euler(0, parts.Length > 5 ? F(parts[5]) : 180, 0);
            foreach (var r in go.GetComponentsInChildren<Renderer>()) Log("  " + a.name + " " + r.name + ": " + string.Join(", ", r.sharedMaterials.Select(m => m != null ? m.name : "null")) + " h=" + r.bounds.size.y.ToString("0.00"));
            var an = go.GetComponentInChildren<Animator>();
            Log("  animator " + (an != null ? (an.runtimeAnimatorController != null ? an.runtimeAnimatorController.name : "no controller") + " avatar=" + (an.avatar != null ? an.avatar.name : "none") : "none") + " scale " + go.transform.lossyScale.x);
        }
        else if (cmd == "sun")
        {
            // sun <pitch> <yaw> <intensity>: an extra key light for looking at models
            var l = new GameObject("probe sun").AddComponent<Light>();
            l.type = LightType.Directional; l.intensity = F(parts[3]); l.transform.rotation = Quaternion.Euler(F(parts[1]), F(parts[2]), 0);
            Log("sun added");
        }
        else if (cmd == "clips")
        {
            foreach (var c in AssetDatabase.LoadAllAssetsAtPath(parts[1]).OfType<AnimationClip>().Where(c => !c.name.StartsWith("__preview")))
                Log("clip " + c.name + " " + c.length.ToString("0.00") + "s loop=" + c.isLooping);
        }
        else if (cmd == "save") { EditorSceneManager.SaveOpenScenes(); Log("saved"); }
        else Log("unknown " + line);
    }

    static IEnumerable<Transform> AllTransforms() =>
        UnityEngine.SceneManagement.SceneManager.GetActiveScene().GetRootGameObjects().SelectMany(g => g.GetComponentsInChildren<Transform>(true));

    static string PathOf(Transform t) { var s = t.name; while (t.parent != null) { t = t.parent; s = t.name + "/" + s; } return s; }

    static string Bounds(Transform t)
    {
        var rs = t.GetComponentsInChildren<Renderer>();
        if (rs.Length == 0) return "";
        var b = rs[0].bounds; foreach (var r in rs) b.Encapsulate(r.bounds);
        return " bounds min=" + V(b.min) + " max=" + V(b.max);
    }

    static void Tree(Transform t, int depth, int level)
    {
        Log(new string(' ', level * 2) + t.name + (t.gameObject.activeInHierarchy ? "" : " (off)") + " pos=" + V(t.position) + " rotY=" + t.eulerAngles.y.ToString("0") + Bounds(t));
        if (level >= depth) return;
        foreach (Transform c in t) Tree(c, depth, level + 1);
    }

    static void Render(string name, System.Action<Camera> setup, int w, int h)
    {
        var go = new GameObject("probe camera");
        try
        {
            var cam = go.AddComponent<Camera>();
            cam.nearClipPlane = .05f; cam.farClipPlane = 600;
            var main = Camera.main;
            if (main != null) { cam.clearFlags = main.clearFlags; cam.backgroundColor = main.backgroundColor; }
            setup(cam);
            var rt = new RenderTexture(w, h, 24, RenderTextureFormat.ARGB32);
            cam.targetTexture = rt;
            cam.Render();
            RenderTexture.active = rt;
            var tex = new Texture2D(w, h, TextureFormat.RGB24, false);
            tex.ReadPixels(new Rect(0, 0, w, h), 0, 0); tex.Apply();
            File.WriteAllBytes(System.IO.Path.Combine(outDir, name + ".png"), tex.EncodeToPNG());
            RenderTexture.active = null; cam.targetTexture = null;
            Object.DestroyImmediate(rt); Object.DestroyImmediate(tex);
            Log("shot " + name);
        }
        finally { Object.DestroyImmediate(go); }
    }
}
