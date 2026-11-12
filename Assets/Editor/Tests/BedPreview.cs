using Mindscape;
using UnityEngine;

// Probe helpers (ShotProbe "method BedPreview.Messy" etc.): show one look of Joey's bed in the open scene, unsaved.
public static class BedPreview
{
    static BedStates Bed => Object.FindAnyObjectByType<BedStates>(FindObjectsInactive.Include);
    static void Show(bool boy, bool girl, bool messy, bool neat)
    {
        var b = Bed; if (b == null) { Debug.Log("[BedPreview] no bed"); return; }
        b.sleepingBoy.SetActive(boy); b.sleepingGirl.SetActive(girl); b.messy.SetActive(messy); b.neat.SetActive(neat);
        Debug.Log("[BedPreview] " + b.transform.position + " rot " + b.transform.eulerAngles + " scale " + b.transform.localScale.x);
    }
    public static void SleepingBoy() => Show(true, false, false, false);
    public static void SleepingGirl() => Show(false, true, false, false);
    public static void Messy() => Show(false, false, true, false);
    public static void Neat() => Show(false, false, false, true);
    // Logs the opening close-up exactly as HouseEpisode computes it (head of the bed = toward the bedside table, -Z here).
    public static void Shots()
    {
        var b = Bed; Vector3 head = Vector3.back;
        b.Face(head, out var face);
        Vector3 close = face - head * 1.9f + Vector3.up * 2.0f + Vector3.Cross(Vector3.up, head) * 1.3f;
        Debug.Log("[BedPreview] face " + face.ToString("F2") + " closeUp " + close.ToString("F2") + " top " + b.Top.ToString("F2"));
    }
}
