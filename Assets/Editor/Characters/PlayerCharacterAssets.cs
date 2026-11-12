using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.Animations;
using UnityEngine;

// The girl the player can choose to play as (PlayerAppearance): NPC_17_Penelope from the NPC roster, with a controller
// that moves like the player's own (Idle / Walk / Run on "Speed" 0, 1, 2, the default state) and also has the story's
// named states (Idle, Talk, Walk, Writing, Seated), so the flashbacks and the mirror can stage a younger her as they
// do younger Joey. Saved to Resources/PlayerCharacters so the runtime can load it.
public static class PlayerCharacterAssets
{
    const string Model = "Assets/Characters/NPCs/NPC_17_Penelope.fbx";   // her animations (and the old model)
    // The outfit lineup (Blender/Blend Files/Main_Character_Outfit_Lineup.blend), exported with the armature named
    // Armature_NPC_17_Penelope so the roster's clips drive it: her home clothes, her school uniform (skirt, the boy's
    // polo and tie, low-cut shoes, no glasses, ponytail) and the school backpack with its straps.
    const string HomeModel = "Assets/Characters/Player/Girl_Home.fbx";
    const string SchoolModel = "Assets/Characters/Player/Girl_School.fbx";
    const string BackpackModel = "Assets/Characters/Player/School_Backpack.fbx";
    const string BackpackPath = Folder + "/Backpack.prefab";
    const string Folder = "Assets/Resources/PlayerCharacters";
    const string ControllerPath = Folder + "/Girl.controller";
    const string PrefabPath = Folder + "/Girl.prefab";

    // The boy from the same lineup (Boy_Default / Boy_School rigs), exported as glTF with the armature named
    // BaldCharacter_Rig like the player's own model, so PlayerAppearance can put his meshes on the player's skeleton.
    const string BoyHomeModel = "Assets/Characters/Player/Boy_Home.glb";
    const string BoySchoolModel = "Assets/Characters/Player/Boy_School.glb";
    const string BoyPrefabPath = Folder + "/Boy.prefab";

    [MenuItem("Mindscape/Player/Build Boy Character")]
    public static void BuildBoy()
    {
        var home = AssetDatabase.LoadAssetAtPath<GameObject>(BoyHomeModel);
        var school = AssetDatabase.LoadAssetAtPath<GameObject>(BoySchoolModel);
        if (home == null || school == null) { Debug.LogError("Missing " + BoyHomeModel + " or " + BoySchoolModel); return; }
        Directory.CreateDirectory(Folder);
        var go = (GameObject)PrefabUtility.InstantiatePrefab(home);
        try
        {
            CombineOutfits(go, school);
            go.name = "Boy";
            foreach (var a in go.GetComponentsInChildren<Animator>(true)) Object.DestroyImmediate(a);
            foreach (var a in go.GetComponentsInChildren<Animation>(true)) Object.DestroyImmediate(a);
            foreach (var c in go.GetComponentsInChildren<Collider>(true)) Object.DestroyImmediate(c);
            PrefabUtility.SaveAsPrefabAsset(go, BoyPrefabPath);
        }
        finally { Object.DestroyImmediate(go); }
        AssetDatabase.SaveAssets();
        Debug.Log("Built " + BoyPrefabPath);
    }

    [MenuItem("Mindscape/Player/Build Girl Character")]
    public static void Build()
    {
        var model = AssetDatabase.LoadAssetAtPath<GameObject>(Model);
        if (model == null) { Debug.LogError("Missing " + Model); return; }
        var clips = AssetDatabase.LoadAllAssetsAtPath(Model).OfType<AnimationClip>().Where(c => !c.name.StartsWith("__preview")).ToArray();
        AnimationClip Clip(string action) => clips.FirstOrDefault(c => c.name.EndsWith("|" + action));
        AnimationClip idle = Clip("Idle"), walk = Clip("Walk"), run = Clip("Run"), talk = Clip("Conversation"), writing = Clip("Sitting_Writing"), seated = Clip("Seated_Idle");
        if (idle == null || walk == null || run == null) { Debug.LogError(Model + " lacks Idle/Walk/Run."); return; }

        Directory.CreateDirectory(Folder);
        AssetDatabase.DeleteAsset(ControllerPath);
        var controller = AnimatorController.CreateAnimatorControllerAtPath(ControllerPath);
        controller.AddParameter("Speed", AnimatorControllerParameterType.Float);
        var machine = controller.layers[0].stateMachine;
        var locomotion = controller.CreateBlendTreeInController("Locomotion", out var tree);
        tree.blendType = BlendTreeType.Simple1D; tree.blendParameter = "Speed"; tree.useAutomaticThresholds = false;
        tree.AddChild(idle, 0); tree.AddChild(walk, 1); tree.AddChild(run, 2);
        machine.defaultState = locomotion;
        void State(string name, AnimationClip clip) { if (clip != null) machine.AddState(name).motion = clip; }
        State("Idle", idle); State("Walk", walk); State("Talk", talk); State("Writing", writing); State("Seated", seated);
        // A named state hands back to moving as soon as the player walks again.
        foreach (var s in machine.states.Select(s => s.state).Where(s => s != locomotion))
        {
            var t = s.AddTransition(locomotion); t.hasExitTime = false; t.duration = .15f;
            t.AddCondition(AnimatorConditionMode.Greater, .1f, "Speed");
        }

        var home = AssetDatabase.LoadAssetAtPath<GameObject>(HomeModel);
        var school = AssetDatabase.LoadAssetAtPath<GameObject>(SchoolModel);
        var go = (GameObject)PrefabUtility.InstantiatePrefab(home != null ? home : model);
        try
        {
            if (home != null && school != null) CombineOutfits(go, school);
            go.name = "Girl";
            var animator = go.GetComponent<Animator>(); if (animator == null) animator = go.AddComponent<Animator>();
            animator.runtimeAnimatorController = controller; animator.applyRootMotion = false;
            animator.cullingMode = AnimatorCullingMode.AlwaysAnimate;
            foreach (var c in go.GetComponentsInChildren<Collider>(true)) Object.DestroyImmediate(c);
            PrefabUtility.SaveAsPrefabAsset(go, PrefabPath);
        }
        finally { Object.DestroyImmediate(go); }
        BuildBackpack();
        AssetDatabase.SaveAssets();
        Debug.Log("Built " + PrefabPath + " and " + ControllerPath);
    }

    // Home and school clothes on one skeleton: every renderer of the home model goes under "Home outfit", the school
    // model's renderers under "School outfit" (re-bound to the home bones by name). PlayerOutfit.Wear shows one.
    static void CombineOutfits(GameObject go, GameObject schoolModel)
    {
        PrefabUtility.UnpackPrefabInstance(go, PrefabUnpackMode.Completely, InteractionMode.AutomatedAction);
        var bones = go.GetComponentsInChildren<Transform>(true).GroupBy(t => t.name).ToDictionary(g => g.Key, g => g.First());
        Transform Group(string name, bool on)
        {
            var g = new GameObject(name).transform;
            g.SetParent(go.transform, false);
            g.gameObject.SetActive(on);
            return g;
        }
        var homeGroup = Group(Mindscape.AcademicPressure.PlayerOutfit.HomeOutfit, true);
        var schoolGroup = Group(Mindscape.AcademicPressure.PlayerOutfit.SchoolOutfit, false);
        foreach (var r in go.GetComponentsInChildren<SkinnedMeshRenderer>(true).ToArray())
            r.transform.SetParent(homeGroup, true);

        var school = (GameObject)PrefabUtility.InstantiatePrefab(schoolModel);
        try
        {
            PrefabUtility.UnpackPrefabInstance(school, PrefabUnpackMode.Completely, InteractionMode.AutomatedAction);
            school.transform.SetPositionAndRotation(go.transform.position, go.transform.rotation);
            foreach (var r in school.GetComponentsInChildren<SkinnedMeshRenderer>(true).ToArray())
            {
                r.bones = r.bones.Select(b => b != null && bones.TryGetValue(b.name, out var t) ? t : null).ToArray();
                if (r.rootBone != null && bones.TryGetValue(r.rootBone.name, out var root)) r.rootBone = root;
                r.transform.SetParent(schoolGroup, true);
            }
        }
        finally { Object.DestroyImmediate(school); }
    }

    // The worn school bag (PlayerBackpack.FromModel reads its skinned pieces and their chest bind pose).
    static void BuildBackpack()
    {
        var model = AssetDatabase.LoadAssetAtPath<GameObject>(BackpackModel);
        if (model == null) { Debug.LogWarning("Missing " + BackpackModel + "; the worn bag stays the built-in boxes."); return; }
        var go = (GameObject)PrefabUtility.InstantiatePrefab(model);
        try
        {
            PrefabUtility.UnpackPrefabInstance(go, PrefabUnpackMode.Completely, InteractionMode.AutomatedAction);
            go.name = "Backpack";
            foreach (var a in go.GetComponentsInChildren<Animator>(true)) Object.DestroyImmediate(a);
            PrefabUtility.SaveAsPrefabAsset(go, BackpackPath);
        }
        finally { Object.DestroyImmediate(go); }
    }
}
