using System.Linq;
using Mindscape.Data;
using UnityEngine;
using UnityEngine.SceneManagement;

// Who the player plays as: the boy (the player rig's own model) or the girl (Resources/PlayerCharacters/Girl, built by
// Mindscape > Player > Build Girl Character). Chosen once before the first story episode (AcademicEpisode asks) and in
// Options > General; kept per profile. Every scene with a player swaps in the chosen model as it loads: the boy's model
// is switched off and the girl stands in its place, driven by the same "Speed" values (Idle / Walk / Run).
public static class PlayerAppearance
{
    public const string GirlName = "Player model (girl)";
    static string Key => MindscapeDatabase.ProfileKey("Mindscape.Character");

    public static bool Chosen => PlayerPrefs.HasKey(Key);
    public static bool IsGirl => PlayerPrefs.GetString(Key, "boy") == "girl";
    public static readonly string[] Names = { "Boy", "Girl" };

    public static void Choose(bool girl)
    {
        PlayerPrefs.SetString(Key, girl ? "girl" : "boy");
        PlayerPrefs.Save();
    }

    /// <summary>The girl model (for the player and for a younger her in the flashbacks), or null.</summary>
    public static GameObject GirlPrefab => Resources.Load<GameObject>("PlayerCharacters/Girl");

    [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.BeforeSceneLoad)]
    static void Install()
    {
        SceneManager.sceneLoaded -= OnLoaded;
        SceneManager.sceneLoaded += OnLoaded;
    }

    static void OnLoaded(Scene scene, LoadSceneMode mode)
    {
        var movement = Object.FindAnyObjectByType<PlayerMovement>(FindObjectsInactive.Include);
        if (movement != null && movement.gameObject.scene == scene) Apply(movement.transform);
    }

    /// <summary>Shows the chosen model on the player and points PlayerMovement at its Animator.</summary>
    public static void Apply(Transform player)
    {
        if (player == null) return;
        var movement = player.GetComponent<PlayerMovement>();
        var girl = player.Find(GirlName);
        // The boy: the rig's own model (every Animator on the player that is not the girl).
        var boy = player.GetComponentsInChildren<Animator>(true).FirstOrDefault(a => girl == null || !a.transform.IsChildOf(girl));
        if (boy != null) DressBoy(boy);
        bool wantGirl = IsGirl;
        if (wantGirl && girl == null && boy != null)
        {
            var prefab = GirlPrefab;
            if (prefab == null) { Debug.LogWarning("Missing Resources/PlayerCharacters/Girl (Mindscape > Player > Build Girl Character)."); wantGirl = false; }
            else girl = Spawn(prefab, player, boy);
        }
        if (boy != null) boy.gameObject.SetActive(!wantGirl);
        if (girl != null) girl.gameObject.SetActive(wantGirl);
        var active = wantGirl && girl != null ? girl.GetComponent<Animator>() : boy;
        if (movement != null && active != null) { movement.animator = active; active.applyRootMotion = false; }
        ShotFocus.Refresh();
    }

    /// <summary>The boy from the outfit lineup (Resources/PlayerCharacters/Boy, Mindscape > Player > Build Boy Character).</summary>
    public static GameObject BoyPrefab => Resources.Load<GameObject>("PlayerCharacters/Boy");

    // The lineup boy shares the player rig's skeleton (same 17 bones, armature BaldCharacter_Rig), so his home and
    // school meshes are moved onto the player's own bones by name and the old single mesh is switched off. The
    // Animator, its clips and everything that looks up the player's bones keep working unchanged.
    public static void DressBoy(Animator boy)
    {
        if (boy == null || boy.transform.Find(Mindscape.AcademicPressure.PlayerOutfit.HomeOutfit) != null) return;
        var prefab = BoyPrefab;
        if (prefab == null) { Debug.LogWarning("Missing Resources/PlayerCharacters/Boy (Mindscape > Player > Build Boy Character)."); return; }
        var old = boy.GetComponentsInChildren<SkinnedMeshRenderer>(true);
        var bones = boy.GetComponentsInChildren<Transform>(true).GroupBy(t => t.name).ToDictionary(g => g.Key, g => g.First());
        var src = Object.Instantiate(prefab);
        try
        {
            src.transform.SetPositionAndRotation(boy.transform.position, boy.transform.rotation);
            src.transform.localScale = boy.transform.lossyScale;
            foreach (Transform group in src.transform.Cast<Transform>().ToArray())
            {
                var renderers = group.GetComponentsInChildren<SkinnedMeshRenderer>(true);
                if (renderers.Length == 0) continue;
                var g = new GameObject(group.name).transform;
                g.SetParent(boy.transform, false);
                g.gameObject.SetActive(group.gameObject.activeSelf);
                g.gameObject.layer = boy.gameObject.layer;
                foreach (var r in renderers)
                {
                    r.bones = r.bones.Select(b => b != null && bones.TryGetValue(b.name, out var t) ? t : null).ToArray();
                    if (r.rootBone != null && bones.TryGetValue(r.rootBone.name, out var root)) r.rootBone = root;
                    r.transform.SetParent(g, true);
                    r.gameObject.layer = boy.gameObject.layer;
                }
            }
        }
        finally { if (Application.isPlaying) Object.Destroy(src); else Object.DestroyImmediate(src); }
        foreach (var r in old) r.gameObject.SetActive(false);
    }

    static Transform Spawn(GameObject prefab, Transform player, Animator boy)
    {
        var girl = Object.Instantiate(prefab, player).transform;
        girl.name = GirlName;
        girl.localPosition = boy.transform.parent == player ? boy.transform.localPosition : Vector3.zero;
        girl.localRotation = Quaternion.identity;
        girl.localScale = Vector3.one;
        // Same height as the boy, feet on the same floor.
        Bounds B(Transform t) { var rs = t.GetComponentsInChildren<Renderer>(true); var b = rs[0].bounds; foreach (var r in rs) b.Encapsulate(r.bounds); return b; }
        if (boy.GetComponentInChildren<Renderer>(true) != null && girl.GetComponentInChildren<Renderer>(true) != null)
        {
            var bb = B(boy.transform); var gb = B(girl);
            if (gb.size.y > .01f) girl.localScale = Vector3.one * (bb.size.y / gb.size.y);
            gb = B(girl);
            girl.position += Vector3.up * (bb.min.y - gb.min.y);
        }
        foreach (var c in girl.GetComponentsInChildren<Collider>(true)) Object.Destroy(c);
        girl.gameObject.layer = boy.gameObject.layer;
        foreach (var t in girl.GetComponentsInChildren<Transform>(true)) t.gameObject.layer = boy.gameObject.layer;
        return girl;
    }
}
