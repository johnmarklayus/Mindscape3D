using System.Linq;
using UnityEngine;

// Probe helper (ShotProbe "method ProbeNear.Ep3Corridor"): logs the renderers whose bounds come within reach of a point,
// with their materials, to find a model part by where it is.
public static class ProbeNear
{
    static void Near(Vector3 p, float reach)
    {
        foreach (var r in Object.FindObjectsByType<Renderer>(FindObjectsSortMode.None))
        {
            var b = r.bounds; if (b.SqrDistance(p) > reach * reach) continue;
            Debug.Log("[ProbeNear] " + r.name + " bounds " + b.min.ToString("F2") + " " + b.max.ToString("F2") + " mats " + string.Join(", ", r.sharedMaterials.Where(m => m != null).Select(m => m.name)));
        }
    }
    public static void Ep3Corridor() => Near(new Vector3(-17f, 1.2f, 2.25f), 4f);
    public static void Ep3Across() { Near(new Vector3(-22f, 1.0f, 8f), 2.5f); Near(new Vector3(-10f, 1.0f, 8f), 2.5f); }
    public static void Ep3Far() { Near(new Vector3(-24f, 1.0f, 11f), 4f); }
    public static void Ep3Wall() { Near(new Vector3(-8f, 1.0f, 0.05f), .6f); Near(new Vector3(6f, 1.0f, 0.05f), .6f); }
}
