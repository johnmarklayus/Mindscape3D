using System.Linq;
using UnityEngine;

namespace Mindscape.AcademicPressure
{
    // Joey's school bag, worn on the back. It is built from a few boxes at runtime and parented to the rig's chest bone,
    // so it moves with the body instead of floating behind the player (the old carried bag was a box on the player's
    // root, which the shirt passed through while walking). The size and the distance from the back are measured from
    // the body mesh in its current pose, so it sits on the shirt without cutting into it.
    // Worn from "Pick up your school bag" in Chapter 1 Episode 1 to the classroom seat in Episode 2, and on the
    // school mornings of Chapter 2.
    public static class PlayerBackpack
    {
        const string Name = "School backpack (worn)";
        static readonly Color Navy = new Color(.15f, .24f, .46f), Pocket = new Color(.78f, .7f, .5f), Strap = new Color(.08f, .11f, .2f);
        static readonly int BaseColorFactor = Shader.PropertyToID("baseColorFactor"), BaseColor = Shader.PropertyToID("_BaseColor");

        static bool Top(Material m) => m != null && (m.name.StartsWith("Shirt") || m.name.Contains("_Shirt") || m.name.Contains("Mat_Top"));

        public static bool IsWorn(Transform player) => Find(player) is Transform t && t.gameObject.activeSelf;

        public static void Wear(Transform player, bool on)
        {
            if (player == null) return;
            var bag = Find(player);
            if (!on) { if (bag != null) bag.gameObject.SetActive(false); return; }
            if (bag == null) bag = FromModel(player) ?? Build(player);
            if (bag != null) bag.gameObject.SetActive(true);
            ShotFocus.Refresh();
        }

        // The model the player is shown as (the boy, or the girl from PlayerAppearance); its chest holds the bag.
        static Transform Body(Transform player)
        {
            var movement = player.GetComponent<PlayerMovement>();
            if (movement != null && movement.animator != null) return movement.animator.transform;
            var a = player.GetComponentsInChildren<Animator>().FirstOrDefault();
            return a != null ? a.transform : player;
        }

        static Transform Find(Transform player)
        {
            var chest = Bone(player, "chest");
            return chest != null ? chest.Find(Name) : null;
        }

        static Transform Bone(Transform player, string name) =>
            Body(player).GetComponentsInChildren<Transform>(true).FirstOrDefault(t => t.name == name);

        // The bag and its two straps from the outfit lineup (Blender/Blend Files/Main_Character_Outfit_Lineup.blend,
        // Resources/PlayerCharacters/Backpack, built by Mindscape > Player > Build Girl Character). The pieces are
        // skinned to the lineup rig's chest only, so they are worn as rigid meshes on the chest bone. Where they go
        // comes from each rig's rest pose (the inverse bind poses), since the boy (glTF) and the girl (FBX) do not
        // share bone axes: piece-on-chest = chestRest⁻¹ · piece, both in the model's own root space.
        static Transform FromModel(Transform player)
        {
            var prefab = Resources.Load<GameObject>("PlayerCharacters/Backpack");
            var body = Body(player);
            var chest = Bone(player, "chest");
            if (prefab == null || chest == null) return null;
            if (!RestInRoot(body, "chest", out var chestRest)) return null;

            var src = Object.Instantiate(prefab);
            src.SetActive(false);
            try
            {
                var root = new GameObject(Name).transform;
                root.SetParent(chest, false);
                foreach (var smr in src.GetComponentsInChildren<SkinnedMeshRenderer>(true))
                {
                    if (smr.sharedMesh == null) continue;
                    var piece = new GameObject(smr.name);
                    piece.layer = player.gameObject.layer;
                    piece.AddComponent<MeshFilter>().sharedMesh = smr.sharedMesh;
                    piece.AddComponent<MeshRenderer>().sharedMaterials = smr.sharedMaterials;
                    // The mesh's own space in the bag model's root space (where the lineup rig stood at rest).
                    Matrix4x4 inRoot = src.transform.worldToLocalMatrix * smr.transform.localToWorldMatrix;
                    Matrix4x4 local = chestRest.inverse * inRoot;
                    piece.transform.SetParent(root, false);
                    piece.transform.localPosition = local.GetColumn(3);
                    piece.transform.localRotation = local.rotation;
                    piece.transform.localScale = local.lossyScale;
                }
                return root;
            }
            finally { Object.Destroy(src); }
        }

        // A bone's rest pose in the model root's space, from any skinned renderer of the model that uses it.
        static bool RestInRoot(Transform model, string bone, out Matrix4x4 rest)
        {
            rest = Matrix4x4.identity;
            foreach (var smr in model.GetComponentsInChildren<SkinnedMeshRenderer>(true))
            {
                if (smr.sharedMesh == null) continue;
                var bones = smr.bones; var poses = smr.sharedMesh.bindposes;
                for (int i = 0; i < bones.Length && i < poses.Length; i++)
                    if (bones[i] != null && bones[i].name == bone)
                    {
                        rest = model.worldToLocalMatrix * smr.transform.localToWorldMatrix * poses[i].inverse;
                        return true;
                    }
            }
            return false;
        }

        static Transform Build(Transform player)
        {
            var chest = Bone(player, "chest");
            var hips = Bone(player, "hips");
            var neck = Bone(player, "neck");
            var armL = Bone(player, "upper_arm.L");
            var armR = Bone(player, "upper_arm.R");
            var skin = Body(player).GetComponentsInChildren<SkinnedMeshRenderer>(true).FirstOrDefault(r => r.sharedMesh != null && r.sharedMaterials.Any(Top));
            if (chest == null || hips == null || neck == null || skin == null) return null;

            Vector3 forward = Vector3.ProjectOnPlane(player.forward, Vector3.up).normalized;
            Vector3 right = Vector3.Cross(Vector3.up, forward);
            float shoulders = armL != null && armR != null ? Mathf.Abs(Vector3.Dot(armL.position - armR.position, right)) : .5f * (neck.position.y - hips.position.y);
            float torso = Mathf.Max(.1f, neck.position.y - hips.position.y);
            Vector3 centre = chest.position;

            // The back and the front of the shirt in this pose, from the body mesh (arms left out).
            var baked = new Mesh();
            skin.BakeMesh(baked, true);
            var toWorld = Matrix4x4.TRS(skin.transform.position, skin.transform.rotation, Vector3.one);
            float back = .18f * torso, front = .18f * torso;
            float yLow = hips.position.y + torso * .25f, yHigh = neck.position.y - torso * .05f;
            foreach (var local in baked.vertices)
            {
                Vector3 v = toWorld.MultiplyPoint3x4(local);
                if (v.y < yLow || v.y > yHigh) continue;
                Vector3 d = v - centre;
                if (Mathf.Abs(Vector3.Dot(d, right)) > shoulders * .32f) continue;
                back = Mathf.Max(back, -Vector3.Dot(d, forward));
                front = Mathf.Max(front, Vector3.Dot(d, forward));
            }
            Object.Destroy(baked);

            var root = new GameObject(Name).transform;
            root.SetPositionAndRotation(new Vector3(centre.x, 0, centre.z), Quaternion.LookRotation(forward));

            float width = shoulders * .78f, height = torso * .92f, depth = width * .5f, gap = torso * .025f;
            float midY = hips.position.y + torso * .5f;
            Vector3 Local(float side, float y, float ahead) => new Vector3(side, y, ahead);   // in the bag's frame (+Z forward)
            var shirt = skin.sharedMaterials.First(Top);
            Material Paint(Color c)
            {
                var m = new Material(shirt) { name = "Backpack" };
                if (m.HasProperty(BaseColorFactor)) m.SetColor(BaseColorFactor, c);
                if (m.HasProperty(BaseColor)) m.SetColor(BaseColor, c);
                m.color = c;
                return m;
            }
            Material body = Paint(Navy), pocket = Paint(Pocket), strap = Paint(Strap);

            void Box(string name, Vector3 at, Vector3 size, Material m, Quaternion? turn = null)
            {
                var b = GameObject.CreatePrimitive(PrimitiveType.Cube);
                Object.Destroy(b.GetComponent<Collider>());
                b.name = name; b.layer = player.gameObject.layer;
                b.transform.SetParent(root, false);
                b.transform.localPosition = at; b.transform.localRotation = turn ?? Quaternion.identity; b.transform.localScale = size;
                b.GetComponent<Renderer>().sharedMaterial = m;
            }
            void Segment(string name, Vector3 a, Vector3 b, float w, float t, Material m)
            {
                Vector3 d = b - a;
                if (d.sqrMagnitude < 1e-6f) return;
                Box(name, (a + b) * .5f, new Vector3(w, t, d.magnitude), m, Quaternion.LookRotation(d, Vector3.up));
            }

            // Right way up at a glance: a darker flap over the top of the outside with a buckle hanging from it, the
            // pocket below it, and the carry loop on top (testers read the old bottom-heavy pocket as an upside-down bag).
            float z = -(back + gap + depth * .5f), outside = z - depth * .5f;
            Box("Bag", Local(0, midY, z), new Vector3(width, height, depth), body);
            Box("Bag top", Local(0, midY + height * .5f, z), new Vector3(width * .9f, height * .07f, depth * .9f), body);
            Box("Flap", Local(0, midY + height * .3f, z - depth * .04f), new Vector3(width * 1.04f, height * .44f, depth * 1.06f), strap);
            Box("Buckle", Local(0, midY + height * .08f, outside - depth * .06f), new Vector3(width * .16f, height * .12f, depth * .06f), pocket);
            Box("Front pocket", Local(0, midY - height * .2f, outside - depth * .12f), new Vector3(width * .64f, height * .32f, depth * .26f), pocket);
            Box("Handle", Local(0, midY + height * .56f, z + depth * .1f), new Vector3(width * .3f, height * .05f, depth * .14f), strap);
            // Two straps from the top of the bag over the shoulders and down the front of the shirt.
            float topY = midY + height * .42f, shoulderY = neck.position.y - torso * .02f;
            foreach (float side in new[] { -1f, 1f })
            {
                float x = side * width * .3f, s = torso * .07f, t = torso * .035f;
                Vector3 onBag = Local(x, topY, -(back + gap));
                Vector3 overShoulder = Local(x, shoulderY + t, -back * .2f);
                Vector3 onChest = Local(x * 1.05f, shoulderY - torso * .05f, front * .55f + t);
                Vector3 low = Local(x * 1.1f, midY - torso * .05f, front + t * .6f);
                Segment("Strap", onBag, overShoulder, s, t, strap);
                Segment("Strap", overShoulder, onChest, s, t, strap);
                Segment("Strap", onChest, low, s, t, strap);
            }
            root.SetParent(chest, true);
            return root;
        }
    }
}
