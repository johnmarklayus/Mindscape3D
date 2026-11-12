using System.Linq;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace Mindscape.SocialDynamics
{
    // Joey's bedroom looks the same in every episode set in the house: the tall mirror on the west wall (the one the
    // Chapter 3 ending walks up to) and the old baseball set beside the wardrobe (the Chapter 2 Episode 5 keepsake)
    // are added to any house scene that does not have them yet, so they are there from the very first morning.
    // They are scenery here: no interaction. The mirror's reflection only renders while you are close to it.
    public static class BedroomDecor
    {
        // The house is the same model at the same place in every house scene; these match SocialDynamicsBuilder
        // (MirrorWall) and KeepsakeBaseball, measured from the "House And Lot" root.
        static readonly Vector3 MirrorFromHouse = new Vector3(3.98f, -.53f, -9.2f);
        const float BaseballScale = 2.4f;

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.BeforeSceneLoad)]
        static void Install()
        {
            SceneManager.sceneLoaded -= Dress;
            SceneManager.sceneLoaded += Dress;
        }

        static void Dress(Scene scene, LoadSceneMode mode)
        {
            var all = scene.GetRootGameObjects().SelectMany(g => g.GetComponentsInChildren<Transform>(true)).ToArray();
            BathroomMirror(all);
            var wardrobe = all.Select(t => t.GetComponent<Renderer>()).FirstOrDefault(r => r != null && r.name == "West bedroom | wardrobe" && r.gameObject.activeInHierarchy);
            var house = all.FirstOrDefault(t => t.parent == null && t.name == "House And Lot");
            if (wardrobe == null || house == null) return;
            var player = Object.FindAnyObjectByType<PlayerMovement>();
            var root = new GameObject("Bedroom decor").transform;
            SceneManager.MoveGameObjectToScene(root.gameObject, scene);
            if (!all.Any(t => t.name == "Mirror surface")) Mirror(root, house.position + MirrorFromHouse, player != null ? player.transform : null);
            if (!all.Any(t => t.name == "Baseball bat" || t.name == "Old hobby item")) Baseball(root, wardrobe.bounds);
        }

        // The house model's bathroom mirror (over the vanity) was a flat grey pane; it reflects like the bedroom one.
        // Which way it faces: toward the middle of the bathroom floor.
        static void BathroomMirror(Transform[] all)
        {
            var glass = all.Select(t => t.GetComponent<Renderer>()).FirstOrDefault(r => r != null && r.name == "Bathroom | mirror");
            if (glass == null || glass.GetComponent<SocialMirror>() != null || glass.GetComponent<MeshFilter>() == null) return;
            var floor = all.Select(t => t.GetComponent<Renderer>()).FirstOrDefault(r => r != null && r.name == "Bathroom | floor tiles");
            var player = Object.FindAnyObjectByType<PlayerMovement>(FindObjectsInactive.Include);
            if (floor == null || player == null) return;
            Bounds b = glass.bounds;
            Vector3 toRoom = floor.bounds.center - b.center;
            bool alongX = b.size.x <= b.size.z;
            float side = (alongX ? toRoom.x : toRoom.z) >= 0 ? 1 : -1;
            Vector3 normal = (alongX ? Vector3.right : Vector3.forward) * side;
            // In the model the frame stands 4 cm proud of the glass and hides all of it, and the wall's tile trim runs
            // across it: bring the glass just in front of anything on the wall that overlaps it.
            float Front(Bounds x) => Vector3.Dot(x.center, normal) + (alongX ? x.extents.x : x.extents.z);
            float glassFront = Front(b), front = glassFront;
            foreach (var r in all.Select(t => t.GetComponent<Renderer>()).Where(r => r != null && r != glass && r.enabled))
            {
                Bounds o = r.bounds;
                bool overlaps = o.min.y < b.max.y && o.max.y > b.min.y
                    && (alongX ? o.min.z < b.max.z && o.max.z > b.min.z : o.min.x < b.max.x && o.max.x > b.min.x);
                float f = Front(o);
                if (overlaps && f > front && f < glassFront + .1f) front = f;
            }
            if (front > glassFront) glass.transform.position += normal * (front + .004f - glassFront);
            var mirror = glass.gameObject.AddComponent<SocialMirror>();
            mirror.player = player.transform;
            mirror.side = side;
            mirror.activeRange = 8;
        }

        static void Mirror(Transform parent, Vector3 wall, Transform player)
        {
            var wood = SocialStaging.Solid(new Color(.42f, .29f, .19f));
            var glass = SocialStaging.Solid(new Color(.55f, .66f, .72f));
            GameObject Box(string name, Vector3 at, Vector3 size, Material m)
            {
                var b = GameObject.CreatePrimitive(PrimitiveType.Cube); Object.Destroy(b.GetComponent<Collider>());
                b.name = name; b.transform.SetParent(parent, false);
                b.transform.position = at; b.transform.localScale = size;
                b.GetComponent<Renderer>().sharedMaterial = m;
                return b;
            }
            Box("Mirror frame", wall + new Vector3(.05f, 2.75f, 0), new Vector3(.12f, 3.6f, 1.65f), wood);
            var surface = Box("Mirror surface", wall + new Vector3(.13f, 2.75f, 0), new Vector3(.015f, 3.34f, 1.4f), glass);
            if (player == null) return;
            var reflection = surface.AddComponent<SocialMirror>();
            reflection.player = player; reflection.planeX = wall.x + .14f; reflection.side = 1; reflection.eyeHeight = 3.4f;
            reflection.activeRange = 9;
        }

        // The glove with the ball in it on the floor beside the wardrobe, and the bat leaning against the wardrobe's side.
        static void Baseball(Transform parent, Bounds w)
        {
            var asset = Resources.Load<GameObject>("Flashback/Baseball set");
            if (asset == null) return;
            var set = Object.Instantiate(asset, parent);
            set.name = "Baseball set (decor)";
            Vector3 floor = new Vector3(w.min.x - .75f, w.min.y, w.min.z + .55f);
            set.transform.SetPositionAndRotation(floor, Quaternion.identity);
            set.transform.localScale = Vector3.one * BaseballScale;
            foreach (var c in set.GetComponentsInChildren<Collider>(true)) Object.Destroy(c);
            Transform Piece(string n) => set.GetComponentsInChildren<Transform>(true).FirstOrDefault(t => t.name == n);
            var glove = Piece("Baseball glove"); var ball = Piece("Baseball"); var bat = Piece("Baseball bat");
            if (glove != null)
            {
                glove.SetPositionAndRotation(floor + new Vector3(-.15f, 0, -.1f), Quaternion.Euler(0, 35, 0));
                var gr = glove.GetComponent<Renderer>();
                if (gr != null)
                {
                    glove.position += Vector3.up * (floor.y - gr.bounds.min.y);
                    var g = gr.bounds;
                    var br = ball != null ? ball.GetComponent<Renderer>() : null;
                    if (br != null) ball.position = new Vector3(g.center.x, g.max.y - .02f, g.center.z) + Vector3.up * (ball.position.y - br.bounds.min.y);
                }
            }
            if (bat != null) bat.SetPositionAndRotation(new Vector3(w.min.x - .55f, w.min.y, w.min.z + 1.05f), Quaternion.AngleAxis(-14, Vector3.forward));
        }
    }
}
