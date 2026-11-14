using System.Collections.Generic;
using System.IO;
using TMPro;
using UnityEngine;

namespace Mindscape.SocialDynamics
{
    // Pieces Chapter 3 builds at runtime, so the scenes need no extra set-up:
    //   LoungeWindow the reunion hall's window by the quiet corner (Episodes 2-6).
    //   CornerSeat   the lounge sofa seat nearest the quiet corner, where Joey sits in Episode 4.
    //   Park         Episode 5's little park with a fountain and lights, where Justin finds Joey.
    //   MemoryFrame  a framed picture with a caption that lights up out of the dark.
    //   DreamSpace   Episode 8's dim, open dream: a path toward a far light, memory frames along both sides.
    //   Capture / Sketch / group photo save: the Episode 6 photograph and the pencil drawing at the very end.
    public static class SocialStaging
    {
        // Good things Joey did without noticing, one per frame: (picture in Resources, words).
        public static readonly (string image, string words)[] Memories =
        {
            ("EpisodeThumbnails/Chapter1_Episode4", "I took one step at a time, even when the deadline felt too big."),
            ("EpisodeThumbnails/Chapter1_Episode3", "I questioned a worried thought, and found a kinder one."),
            ("EpisodeThumbnails/Chapter2_Episode4", "I told my family how I really felt."),
            ("FamilyFinale/Keepsake_Certificate", "I was proud of myself once, just for trying."),
            ("EpisodeThumbnails/Chapter3_Episode2", "I went to the reunion, even though I was scared."),
            ("EpisodeThumbnails/Chapter3_Episode5", "I let a friend in when he checked on me."),
            (GroupPhotoKey, "I came back to the group, just as I am."),
        };
        public const string GroupPhotoKey = "@group-photo";

        static Material litDark, frameGold, unlitBase;
        static Shader Lit => Shader.Find("Universal Render Pipeline/Lit");
        static Shader Unlit => Shader.Find("Universal Render Pipeline/Unlit");

        public static Material Solid(Color color, bool unlit = false)
        {
            var m = new Material(unlit ? Unlit : Lit);
            m.SetColor("_BaseColor", color); m.color = color;
            return m;
        }

        public static Texture2D Picture(string key)
        {
            if (key == GroupPhotoKey) return LoadGroupPhoto() ?? Resources.Load<Texture2D>("SocialDynamics/OldGroupPhoto");
            return Resources.Load<Texture2D>(key);
        }

        // ---------------------------------------------------------------- memory frames

        public static MemoryFrame Frame(Transform parent, Vector3 at, Vector3 facing, Texture2D picture, string words, float width = 2.4f)
        {
            // Quads and TMP text face -Z, so the frame's +Z points away from the viewer ('facing' points toward them).
            var root = new GameObject("Memory · " + words).transform;
            root.SetParent(parent, true); root.position = at; root.rotation = Quaternion.LookRotation(-facing.normalized);
            float height = width * 9f / 16f;
            if (picture != null && picture.width > 0) height = width * picture.height / (float)picture.width;
            if (frameGold == null) frameGold = Solid(new Color(.86f, .7f, .42f), true);
            var border = GameObject.CreatePrimitive(PrimitiveType.Quad); Object.Destroy(border.GetComponent<Collider>());
            border.name = "Frame"; border.transform.SetParent(root, false);
            border.transform.localPosition = new Vector3(0, 0, .01f); border.transform.localScale = new Vector3(width + .16f, height + .16f, 1);
            var borderMat = new Material(frameGold); border.GetComponent<Renderer>().sharedMaterial = borderMat;
            var quad = GameObject.CreatePrimitive(PrimitiveType.Quad); Object.Destroy(quad.GetComponent<Collider>());
            quad.name = "Picture"; quad.transform.SetParent(root, false); quad.transform.localScale = new Vector3(width, height, 1);
            var pictureMat = Solid(Color.white, true);
            if (picture != null) { pictureMat.SetTexture("_BaseMap", picture); pictureMat.mainTexture = picture; }
            quad.GetComponent<Renderer>().sharedMaterial = pictureMat;
            foreach (var r in root.GetComponentsInChildren<Renderer>()) { r.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off; r.receiveShadows = false; }

            var caption = new GameObject("Caption").AddComponent<TextMeshPro>();
            caption.transform.SetParent(root, false); caption.transform.localPosition = new Vector3(0, -height * .5f - .38f, 0);
            caption.text = words; caption.fontSize = 2.2f; caption.alignment = TextAlignmentOptions.Center;
            caption.rectTransform.sizeDelta = new Vector2(width + 1.4f, 1.2f); caption.color = new Color(1, .95f, .85f, 0);

            var glow = new GameObject("Glow").AddComponent<Light>();
            glow.transform.SetParent(root, false); glow.transform.localPosition = new Vector3(0, 0, -1.2f);
            glow.type = LightType.Point; glow.color = new Color(1, .86f, .62f); glow.range = 6; glow.intensity = 0; glow.shadows = LightShadows.None;

            var frame = root.gameObject.AddComponent<MemoryFrame>();
            frame.Init(pictureMat, borderMat, caption, glow);
            return frame;
        }

        // ---------------------------------------------------------------- the dream

        public static DreamSpace Dream(Vector3 origin, float length)
        {
            var root = new GameObject("Dream space").transform; root.position = origin;
            if (litDark == null) litDark = Solid(new Color(.07f, .09f, .15f));
            // The floor: a long dark path with no walls or ceiling; it fades into the dark at its edges.
            var floor = GameObject.CreatePrimitive(PrimitiveType.Cube); floor.name = "Dream floor";
            floor.transform.SetParent(root, false); floor.transform.localPosition = new Vector3(0, -.25f, length * .5f - 6);
            floor.transform.localScale = new Vector3(40, .5f, length + 24); floor.GetComponent<Renderer>().sharedMaterial = litDark;
            var path = GameObject.CreatePrimitive(PrimitiveType.Cube); path.name = "Faint path"; Object.Destroy(path.GetComponent<Collider>());
            path.transform.SetParent(root, false); path.transform.localPosition = new Vector3(0, .005f, length * .5f);
            path.transform.localScale = new Vector3(3.2f, .01f, length); path.GetComponent<Renderer>().sharedMaterial = Solid(new Color(.16f, .2f, .32f));
            // Invisible walls keep you on the way forward without boxing the view in.
            void Wall(Vector3 at, Vector3 size)
            {
                var w = new GameObject("Dream edge", typeof(BoxCollider)).transform; w.SetParent(root, false);
                w.localPosition = at; w.GetComponent<BoxCollider>().size = size;
            }
            Wall(new Vector3(-7, 3, length * .5f), new Vector3(.5f, 6, length + 24));
            Wall(new Vector3(7, 3, length * .5f), new Vector3(.5f, 6, length + 24));
            Wall(new Vector3(0, 3, -6), new Vector3(14, 6, .5f));
            Wall(new Vector3(0, 3, length + 4), new Vector3(14, 6, .5f));
            // The light far ahead: an open, glowing doorway standing on its own (not a tunnel), with a few steps up to it.
            var door = new GameObject("Distant light").transform; door.SetParent(root, false); door.localPosition = new Vector3(0, 0, length);
            var white = Solid(new Color(1.6f, 1.55f, 1.4f), true);
            var stone = Solid(new Color(.35f, .45f, .7f), true);
            for (int i = 0; i < 4; i++)
            {
                var step = GameObject.CreatePrimitive(PrimitiveType.Cube); step.name = "Step"; Object.Destroy(step.GetComponent<Collider>());
                step.transform.SetParent(door, false); step.transform.localPosition = new Vector3(0, .1f + i * .2f, -2.4f + i * .55f);
                step.transform.localScale = new Vector3(5 - i * .5f, .2f, .6f); step.GetComponent<Renderer>().sharedMaterial = stone;
            }
            foreach (float x in new[] { -1.7f, 1.7f })
            {
                var pillar = GameObject.CreatePrimitive(PrimitiveType.Cube); pillar.name = "Pillar"; Object.Destroy(pillar.GetComponent<Collider>());
                pillar.transform.SetParent(door, false); pillar.transform.localPosition = new Vector3(x, 3.4f, 0); pillar.transform.localScale = new Vector3(.4f, 5.6f, .4f);
                pillar.GetComponent<Renderer>().sharedMaterial = stone;
            }
            var arch = GameObject.CreatePrimitive(PrimitiveType.Cube); arch.name = "Arch"; Object.Destroy(arch.GetComponent<Collider>());
            arch.transform.SetParent(door, false); arch.transform.localPosition = new Vector3(0, 6.3f, 0); arch.transform.localScale = new Vector3(3.8f, .4f, .4f);
            arch.GetComponent<Renderer>().sharedMaterial = stone;
            var glowPane = GameObject.CreatePrimitive(PrimitiveType.Quad); glowPane.name = "Light in the doorway"; Object.Destroy(glowPane.GetComponent<Collider>());
            glowPane.transform.SetParent(door, false); glowPane.transform.localPosition = new Vector3(0, 3.4f, .05f); glowPane.transform.localScale = new Vector3(3, 5.6f, 1);
            glowPane.GetComponent<Renderer>().sharedMaterial = white;
            var light = new GameObject("Doorway light").AddComponent<Light>(); light.transform.SetParent(door, false); light.transform.localPosition = new Vector3(0, 3, -2);
            light.type = LightType.Point; light.color = new Color(.85f, .9f, 1); light.intensity = 6; light.range = 30; light.shadows = LightShadows.None;
            foreach (var r in root.GetComponentsInChildren<Renderer>()) r.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;

            var dream = root.gameObject.AddComponent<DreamSpace>();
            dream.start = new GameObject("Dream start").transform; dream.start.SetParent(root, false); dream.start.localPosition = new Vector3(0, .1f, 0);
            dream.end = door; dream.length = length; dream.doorwayLight = light;
            // Memory frames on alternating sides of the path, angled toward you as you walk.
            var frames = new List<MemoryFrame>();
            for (int i = 0; i < Memories.Length; i++)
            {
                float z = 10 + i * (length - 18) / Mathf.Max(1, Memories.Length - 1);
                float x = i % 2 == 0 ? -3.6f : 3.6f;
                Vector3 at = origin + new Vector3(x, 2.6f, z);
                Vector3 facing = new Vector3(-x * .6f, 0, -1);   // toward the path and back toward you
                frames.Add(Frame(root, at, facing, Picture(Memories[i].image), Memories[i].words));
            }
            dream.frames = frames.ToArray();
            return dream;
        }

        // ---------------------------------------------------------------- the corner seat

        // Episode 4 "Sit by the window": the hall's lounge furniture is one merged mesh, so the seat is found by its shape.
        // The floor round 'spot' is sampled from above; a seat is a flat patch at chair height with a backrest right
        // behind it (and the same cushion height to both sides, so not an armrest). Returns the seat cell nearest 'spot':
        // 'seatTop' is the top of the cushion, 'facing' points away from the backrest.
        public static bool CornerSeat(Vector3 spot, out Vector3 seatTop, out Vector3 facing, float radius = 6f)
        {
            seatTop = spot; facing = Vector3.forward;
            float floorY = spot.y;
            if (Physics.Raycast(spot + Vector3.up, Vector3.down, out var floorHit, 6, ~0, QueryTriggerInteraction.Ignore)) floorY = floorHit.point.y;
            const float step = .1f;
            int n = Mathf.CeilToInt(radius / step);
            var top = new float[2 * n + 1, 2 * n + 1];
            for (int i = -n; i <= n; i++)
                for (int j = -n; j <= n; j++)
                {
                    float best = float.NegativeInfinity;
                    var o = new Vector3(spot.x + i * step, floorY + 2.2f, spot.z + j * step);
                    foreach (var hit in Physics.RaycastAll(o, Vector3.down, 3f, ~0, QueryTriggerInteraction.Ignore))
                        if (hit.collider.GetComponentInParent<CharacterController>() == null) best = Mathf.Max(best, hit.point.y);
                    top[i + n, j + n] = best - floorY;
                }
            float H(int i, int j) => i < -n || i > n || j < -n || j > n ? float.NegativeInfinity : top[i + n, j + n];
            var dirs = new[] { (1, 0), (-1, 0), (0, 1), (0, -1) };
            float bestDistance = float.MaxValue; bool found = false;
            for (int i = -n; i <= n; i++)
                for (int j = -n; j <= n; j++)
                {
                    float h = H(i, j);
                    if (h < .3f || h > .7f) continue;
                    foreach (var (di, dj) in dirs)
                    {
                        // Backrest within 0.6 m behind, clearly higher than the cushion.
                        int back = 0;
                        for (int k = 1; k <= 6 && back == 0; k++) if (H(i + di * k, j + dj * k) > h + .35f && H(i + di * k, j + dj * k) < h + 1.1f) back = k;
                        if (back == 0) continue;
                        // The same cushion 0.4 m to both sides and for 0.5 m in front: the middle of a seat, not an armrest
                        // (an armrest top is as high as a cushion, but has no seat depth in front of it).
                        bool flat = true;
                        foreach (int side in new[] { -4, 4 }) flat &= Mathf.Abs(H(i + dj * side, j + di * side) - h) < .04f;
                        for (int k = 1; k <= 5 && flat; k++) flat &= Mathf.Abs(H(i - di * k, j - dj * k) - h) < .04f;
                        if (!flat) continue;
                        float distance = new Vector2(i, j).magnitude;
                        if (distance >= bestDistance) continue;
                        bestDistance = distance; found = true;
                        facing = new Vector3(-di, 0, -dj);
                        // Hips about 0.28 m in front of the backrest's face (it starts half a cell before cell 'back').
                        seatTop = new Vector3(spot.x + i * step, floorY + h, spot.z + j * step) + facing * (.28f - (back - .5f) * step);
                    }
                }
            return found;
        }

        // ---------------------------------------------------------------- the lounge window

        // "Sit by the window": the hall's lounge corner had only photo boards on a plain wall. This puts a real window on
        // the wall nearest 'spot': a wooden frame with four panes onto the evening city, a sill and curtains. The wall is
        // scanned first: a lower wall panel (wainscot) becomes the ledge the window sits on, and any board the window
        // lands on is covered completely (the window grows over it) so nothing pokes out round its edges.
        public static Transform LoungeWindow(Transform parent, Vector3 spot)
        {
            float floorY = spot.y;
            if (Physics.Raycast(spot + Vector3.up, Vector3.down, out var floorHit, 6, ~0, QueryTriggerInteraction.Ignore)) floorY = floorHit.point.y;
            Vector3 foot = new Vector3(spot.x, floorY, spot.z);
            // The nearest wall of the hall itself.
            Vector3 outward = Vector3.left; float near = float.MaxValue;
            foreach (var dir in new[] { Vector3.left, Vector3.right, Vector3.forward, Vector3.back })
                foreach (var hit in Physics.RaycastAll(foot + Vector3.up * 4f, dir, 10, ~0, QueryTriggerInteraction.Ignore))
                    if (hit.collider.name.Contains("Architecture") && hit.distance < near) { near = hit.distance; outward = dir; }
            if (near == float.MaxValue) return null;
            Vector3 along = Vector3.Cross(Vector3.up, outward);
            // Scan the wall: distance to whatever is hit, on a grid across it.
            const float step = .25f;
            int nu = 33, nv = 25;   // u: -4..4 along the wall, v: 0.5..6.5 up
            var depth = new float[nu, nv];
            float wall = 0;
            for (int i = 0; i < nu; i++)
                for (int j = 0; j < nv; j++)
                {
                    Vector3 o = foot + along * (-4 + i * step) + Vector3.up * (.5f + j * step);
                    depth[i, j] = Physics.Raycast(o, outward, out var h, near + 3, ~0, QueryTriggerInteraction.Ignore) ? h.distance : near + 3;
                    if (depth[i, j] < near + 2.5f) wall = Mathf.Max(wall, depth[i, j]);
                }
            // On the wall: a board or a panel (furniture standing out in the room, like the sofa, does not count).
            bool Proud(int i, int j) => depth[i, j] < wall - .08f && depth[i, j] > wall - .9f;
            // The ledge: the highest row (below 3.2 up) where almost the whole width stands proud of the wall.
            int ledge = -1;
            for (int j = 0; j < nv && .5f + j * step < 3.2f; j++)
            {
                int count = 0; for (int i = 0; i < nu; i++) if (Proud(i, j)) count++;
                if (count > nu * .85f) ledge = j;
            }
            float bottom = ledge >= 0 ? .5f + (ledge + 1) * step + .1f : 1.7f;
            float uMin = -1.8f, uMax = 1.8f, vMin = bottom, vMax = bottom + 2.7f;
            // Grow over any board it overlaps (not the ledge rows).
            for (int pass = 0; pass < 6; pass++)
            {
                bool grew = false;
                for (int i = 0; i < nu; i++)
                    for (int j = ledge + 1; j < nv; j++)
                    {
                        if (!Proud(i, j)) continue;
                        float u = -4 + i * step, v = .5f + j * step;
                        bool touches = u >= uMin - step && u <= uMax + step && v >= vMin - step && v <= vMax + step;
                        if (!touches || (u >= uMin && u <= uMax && v >= vMin && v <= vMax)) continue;
                        uMin = Mathf.Min(uMin, u - .2f); uMax = Mathf.Max(uMax, u + .2f); vMax = Mathf.Min(6.4f, Mathf.Max(vMax, v + .2f));
                        grew = true;
                    }
                if (!grew) break;
            }
            // In front of everything it covers.
            float face = wall;
            for (int i = 0; i < nu; i++)
                for (int j = Mathf.Max(0, ledge + 1); j < nv; j++)
                {
                    float u = -4 + i * step, v = .5f + j * step;
                    if (u >= uMin - .1f && u <= uMax + .1f && v >= vMin - .1f && v <= vMax + .1f && depth[i, j] > wall - .9f) face = Mathf.Min(face, depth[i, j]);
                }
            float width = uMax - uMin, height = vMax - vMin;
            Vector3 centre = foot + outward * (face - .06f) + along * ((uMin + uMax) * .5f) + Vector3.up * ((vMin + vMax) * .5f);

            var root = new GameObject("Lounge window").transform; root.SetParent(parent, true);
            root.SetPositionAndRotation(centre, Quaternion.LookRotation(-outward));   // local +Z faces into the room
            var wood = Solid(new Color(.36f, .25f, .17f)); var paint = Solid(new Color(.93f, .91f, .86f));
            var cloth = Solid(new Color(.55f, .27f, .24f)); var view = Solid(Color.white, true);
            view.SetTexture("_BaseMap", EveningCity()); view.mainTexture = view.GetTexture("_BaseMap");
            GameObject Box(string name, Vector3 local, Vector3 size, Material m)
            {
                var go = GameObject.CreatePrimitive(PrimitiveType.Cube); Object.Destroy(go.GetComponent<Collider>());
                go.name = name; go.transform.SetParent(root, false); go.transform.localPosition = local; go.transform.localScale = size;
                go.GetComponent<Renderer>().sharedMaterial = m; return go;
            }
            // The view: a quad a little behind the frame, so the bars have depth.
            var pane = GameObject.CreatePrimitive(PrimitiveType.Quad); Object.Destroy(pane.GetComponent<Collider>());
            pane.name = "Evening view"; pane.transform.SetParent(root, false);
            pane.transform.localPosition = new Vector3(0, 0, -.02f); pane.transform.localRotation = Quaternion.Euler(0, 180, 0);
            pane.transform.localScale = new Vector3(width, height, 1);
            pane.GetComponent<Renderer>().sharedMaterial = view;
            Box("Window back", new Vector3(0, 0, -.05f), new Vector3(width + .1f, height + .1f, .04f), paint);
            float bar = .14f, deep = .16f;
            Box("Frame top", new Vector3(0, height * .5f, deep * .5f), new Vector3(width + bar * 2, bar, deep), wood);
            Box("Frame bottom", new Vector3(0, -height * .5f, deep * .5f), new Vector3(width + bar * 2, bar, deep), wood);
            Box("Frame left", new Vector3(-width * .5f, 0, deep * .5f), new Vector3(bar, height, deep), wood);
            Box("Frame right", new Vector3(width * .5f, 0, deep * .5f), new Vector3(bar, height, deep), wood);
            Box("Mullion", new Vector3(0, 0, deep * .4f), new Vector3(bar * .6f, height, deep * .8f), wood);
            Box("Transom", new Vector3(0, height * .12f, deep * .4f), new Vector3(width, bar * .6f, deep * .8f), wood);
            Box("Sill", new Vector3(0, -height * .5f - bar * .5f, .22f), new Vector3(width + .5f, .1f, .44f), paint);
            Box("Curtain rod", new Vector3(0, height * .5f + .35f, .3f), new Vector3(width + 1.4f, .06f, .06f), wood);
            foreach (float side in new[] { -1f, 1f })
                Box("Curtain", new Vector3(side * (width * .5f + .3f), .1f, .3f), new Vector3(.6f, height + .7f, .12f), cloth);
            foreach (var r in root.GetComponentsInChildren<Renderer>()) r.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
            // Cool evening light coming in.
            var light = new GameObject("Window light").AddComponent<Light>(); light.transform.SetParent(root, false);
            light.transform.localPosition = new Vector3(0, 0, 1.6f); light.type = LightType.Point; light.color = new Color(.62f, .7f, 1f);
            light.intensity = 1.2f; light.range = 7; light.shadows = LightShadows.None;
            return root;
        }

        // A painted evening city for the window: the sky darkening upward, a row of buildings with lit windows, the moon.
        static Texture2D eveningCity;
        static Texture2D EveningCity()
        {
            if (eveningCity != null) return eveningCity;
            const int w = 256, h = 192;
            var px = new Color[w * h];
            Color top = new Color(.06f, .09f, .22f), horizon = new Color(.55f, .4f, .52f);
            for (int y = 0; y < h; y++)
            {
                float k = Mathf.Pow(y / (float)(h - 1), .8f);
                var sky = Color.Lerp(horizon, top, k);
                for (int x = 0; x < w; x++) px[y * w + x] = sky;
            }
            var random = new System.Random(7);
            for (int i = 0; i < 40; i++) { int x = random.Next(w), y = h / 2 + random.Next(h / 2); px[y * w + x] = new Color(.9f, .9f, 1f); }
            // The moon.
            for (int y = -9; y <= 9; y++) for (int x = -9; x <= 9; x++) if (x * x + y * y <= 81) px[(150 + y) * w + 200 + x] = new Color(.98f, .95f, .82f);
            // Two rows of buildings, the far one paler.
            for (int row = 0; row < 2; row++)
            {
                int x = -random.Next(20);
                var body = row == 0 ? new Color(.2f, .2f, .32f) : new Color(.08f, .09f, .15f);
                while (x < w)
                {
                    int bw = 18 + random.Next(26), bh = (row == 0 ? 60 : 30) + random.Next(row == 0 ? 50 : 55);
                    for (int bx = Mathf.Max(0, x); bx < Mathf.Min(w, x + bw); bx++)
                        for (int by = 0; by < bh; by++) px[by * w + bx] = body;
                    if (row == 1)
                        for (int wy = 6; wy < bh - 6; wy += 9)
                            for (int wx = x + 4; wx < x + bw - 4; wx += 7)
                                if (random.NextDouble() < .45)
                                    for (int a = 0; a < 3; a++) for (int b = 0; b < 4; b++)
                                    {
                                        int fx = wx + a, fy = wy + b;
                                        if (fx >= 0 && fx < w && fy < h) px[fy * w + fx] = new Color(1f, .82f, .45f);
                                    }
                    x += bw + random.Next(4);
                }
            }
            eveningCity = new Texture2D(w, h, TextureFormat.RGB24, false) { wrapMode = TextureWrapMode.Clamp };
            eveningCity.SetPixels(px); eveningCity.Apply();
            return eveningCity;
        }

        // ---------------------------------------------------------------- the little park

        // Episode 5: a small park outside the reunion, where Joey goes for some air and Justin comes to find him. A paved
        // circle round a fountain, lamp posts with warm string lights between them, a bench, hedges and trees, and a path
        // in. It is built well away from everything else (so nothing of the city pokes into it) and destroyed after.
        public static ParkSpace Park(Vector3 origin)
        {
            var root = new GameObject("Little park").transform; root.position = origin;
            var grass = Solid(new Color(.2f, .33f, .2f)); var stone = Solid(new Color(.6f, .58f, .55f)); var paving = Solid(new Color(.5f, .48f, .45f));
            var water = Solid(new Color(.25f, .5f, .7f)); var iron = Solid(new Color(.12f, .13f, .14f)); var wood = Solid(new Color(.45f, .3f, .19f));
            var leaf = Solid(new Color(.18f, .36f, .22f)); var dark = Solid(new Color(.14f, .27f, .17f)); var bark = Solid(new Color(.32f, .22f, .15f));
            var bulb = Solid(new Color(1.8f, 1.35f, .7f), true); var lampGlass = Solid(new Color(1.6f, 1.3f, .8f), true);
            GameObject Part(string name, PrimitiveType type, Vector3 local, Vector3 size, Material m, bool solid = false, Quaternion? turn = null)
            {
                var go = GameObject.CreatePrimitive(type); go.name = name;
                if (!solid) Object.Destroy(go.GetComponent<Collider>());
                go.transform.SetParent(root, false); go.transform.localPosition = local; go.transform.localScale = size;
                go.transform.localRotation = turn ?? Quaternion.identity;
                go.GetComponent<Renderer>().sharedMaterial = m; return go;
            }
            Part("Lawn", PrimitiveType.Cube, new Vector3(0, -.25f, 0), new Vector3(90, .5f, 90), grass, true);
            Part("Plaza", PrimitiveType.Cylinder, new Vector3(0, .01f, 0), new Vector3(17, .02f, 17), paving);
            Part("Path", PrimitiveType.Cube, new Vector3(0, .012f, -16), new Vector3(3.4f, .02f, 18), paving);
            // The fountain.
            Part("Fountain basin", PrimitiveType.Cylinder, new Vector3(0, .5f, 0), new Vector3(7, .5f, 7), stone, true);
            Part("Fountain water", PrimitiveType.Cylinder, new Vector3(0, .96f, 0), new Vector3(6.3f, .02f, 6.3f), water);
            Part("Fountain column", PrimitiveType.Cylinder, new Vector3(0, 1.6f, 0), new Vector3(.8f, 1.6f, .8f), stone);
            Part("Fountain bowl", PrimitiveType.Cylinder, new Vector3(0, 3.1f, 0), new Vector3(2.6f, .18f, 2.6f), stone);
            Part("Fountain spout", PrimitiveType.Sphere, new Vector3(0, 3.6f, 0), new Vector3(.7f, 1f, .7f), water);
            var fountainGlow = new GameObject("Fountain light").AddComponent<Light>(); fountainGlow.transform.SetParent(root, false);
            fountainGlow.transform.localPosition = new Vector3(0, 1.4f, 0); fountainGlow.type = LightType.Point; fountainGlow.color = new Color(.55f, .75f, 1f);
            fountainGlow.intensity = 1.5f; fountainGlow.range = 6; fountainGlow.shadows = LightShadows.None;
            // Lamp posts round the plaza, leaving the path (south) open, with string lights between neighbours.
            var tops = new List<Vector3>();
            for (int i = 0; i < 6; i++)
            {
                float a = (i * 60f + 30f) * Mathf.Deg2Rad;
                Vector3 at = new Vector3(Mathf.Sin(a), 0, Mathf.Cos(a)) * 9.2f;
                Part("Lamp post", PrimitiveType.Cylinder, at + Vector3.up * 2.6f, new Vector3(.22f, 2.6f, .22f), iron);
                Part("Lamp", PrimitiveType.Sphere, at + Vector3.up * 5.4f, Vector3.one * .7f, lampGlass);
                var l = new GameObject("Lamp light").AddComponent<Light>(); l.transform.SetParent(root, false);
                l.transform.localPosition = at + Vector3.up * 5f; l.type = LightType.Point; l.color = new Color(1f, .8f, .55f);
                l.intensity = 2.2f; l.range = 11; l.shadows = LightShadows.None;
                tops.Add(at + Vector3.up * 5.1f);
            }
            for (int i = 0; i < tops.Count; i++)
            {
                Vector3 a = tops[i], b = tops[(i + 1) % tops.Count];
                if (i == 2) continue;   // over the path: no strand, the way in stays open to the sky
                for (int k = 1; k < 10; k++)
                {
                    float t = k / 10f;
                    Part("String bulb", PrimitiveType.Sphere, Vector3.Lerp(a, b, t) + Vector3.down * Mathf.Sin(t * Mathf.PI) * .9f, Vector3.one * .2f, bulb);
                }
            }
            // A bench facing the fountain, beside where Joey stands.
            Vector3 bench = new Vector3(-5.6f, 0, -4.4f); var benchTurn = Quaternion.LookRotation(-bench.normalized);
            Part("Bench seat", PrimitiveType.Cube, bench + Vector3.up * 1.05f, new Vector3(3.6f, .14f, 1.05f), wood, true, benchTurn);
            Part("Bench back", PrimitiveType.Cube, bench + benchTurn * new Vector3(0, 1.75f, -.48f), new Vector3(3.6f, .9f, .1f), wood, false, benchTurn);
            foreach (float x in new[] { -1.5f, 1.5f })
                Part("Bench leg", PrimitiveType.Cube, bench + benchTurn * new Vector3(x, .5f, 0), new Vector3(.12f, 1f, .9f), iron, false, benchTurn);
            // Hedges round the edge (open at the path) and trees beyond them.
            for (int i = 0; i < 20; i++)
            {
                float a = i * 18f;
                if (a > 160 && a < 200) continue;
                float r = a * Mathf.Deg2Rad; Vector3 at = new Vector3(Mathf.Sin(r), 0, Mathf.Cos(r)) * 13.5f;
                Part("Hedge", PrimitiveType.Cube, at + Vector3.up * .9f, new Vector3(4.3f, 1.8f, 1.3f), dark, true, Quaternion.LookRotation(at));
            }
            var random = new System.Random(11);
            for (int i = 0; i < 16; i++)
            {
                float a = i * 22.5f + (float)random.NextDouble() * 9;
                if (a > 150 && a < 210) continue;
                float r = a * Mathf.Deg2Rad, d = 17 + (float)random.NextDouble() * 6;
                Vector3 at = new Vector3(Mathf.Sin(r), 0, Mathf.Cos(r)) * d;
                float tall = 5 + (float)random.NextDouble() * 3;
                Part("Tree trunk", PrimitiveType.Cylinder, at + Vector3.up * tall * .5f, new Vector3(.6f, tall * .5f, .6f), bark);
                Part("Tree crown", PrimitiveType.Sphere, at + Vector3.up * (tall + 1.2f), Vector3.one * (4 + (float)random.NextDouble() * 2), leaf);
            }
            foreach (var r in root.GetComponentsInChildren<Renderer>())
                if (r.sharedMaterial == bulb || r.sharedMaterial == lampGlass) r.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
            var park = root.gameObject.AddComponent<ParkSpace>();
            park.fountain = origin;
            park.joey = origin + new Vector3(-1.4f, 0, -5.4f);
            park.justinFrom = origin + new Vector3(1.2f, 0, -22f);
            park.justinTo = origin + new Vector3(1.6f, 0, -5.1f);
            return park;
        }

        // ---------------------------------------------------------------- pictures

        public static Texture2D Capture(Camera camera, int width, int height)
        {
            var rt = RenderTexture.GetTemporary(width, height, 24);
            var previous = RenderTexture.active; var oldTarget = camera.targetTexture;
            var image = new Texture2D(width, height, TextureFormat.RGB24, false);
            try
            {
                camera.targetTexture = rt; camera.Render();
                RenderTexture.active = rt; image.ReadPixels(new Rect(0, 0, width, height), 0, 0); image.Apply();
            }
            finally { camera.targetTexture = oldTarget; RenderTexture.active = previous; RenderTexture.ReleaseTemporary(rt); }
            return image;
        }

        // A pencil drawing of what the camera sees: soft graphite shading plus dark edges on warm paper.
        public static Texture2D Sketch(Camera camera, int width = 960, int height = 540)
        {
            var photo = Capture(camera, width, height);
            var src = photo.GetPixels(); Object.Destroy(photo);
            var lum = new float[src.Length];
            for (int i = 0; i < src.Length; i++) lum[i] = src[i].r * .3f + src[i].g * .59f + src[i].b * .11f;
            // Normalise the brightness so a dim room still draws with a full range of tones.
            float lo = 1, hi = 0; foreach (var l in lum) { lo = Mathf.Min(lo, l); hi = Mathf.Max(hi, l); }
            float span = Mathf.Max(.05f, hi - lo);
            var outPx = new Color[src.Length];
            var paper = new Color(.96f, .93f, .86f); var graphite = new Color(.22f, .2f, .19f);
            for (int y = 0; y < height; y++)
                for (int x = 0; x < width; x++)
                {
                    int i = y * width + x;
                    float L(int dx, int dy) => (lum[Mathf.Clamp(y + dy, 0, height - 1) * width + Mathf.Clamp(x + dx, 0, width - 1)] - lo) / span;
                    float gx = -L(-1, -1) - 2 * L(-1, 0) - L(-1, 1) + L(1, -1) + 2 * L(1, 0) + L(1, 1);
                    float gy = -L(-1, -1) - 2 * L(0, -1) - L(1, -1) + L(-1, 1) + 2 * L(0, 1) + L(1, 1);
                    float edge = Mathf.Clamp01(Mathf.Sqrt(gx * gx + gy * gy) * 1.6f - .08f);
                    float tone = L(0, 0);
                    // Light hatching in the darker areas: diagonal lines whose density follows the shade.
                    float hatch = tone < .55f && ((x + y) % 6 == 0) ? (.55f - tone) * .9f : 0;
                    hatch += tone < .3f && ((x - y + 1000) % 6 == 0) ? (.3f - tone) * .9f : 0;
                    float ink = Mathf.Clamp01(edge + hatch + (1 - tone) * .12f);
                    // A soft vignette, like a drawing that fades toward the edges of the page.
                    float vx = x / (float)width - .5f, vy = y / (float)height - .5f;
                    float fade = Mathf.Clamp01(1 - (vx * vx + vy * vy) * 2.2f);
                    outPx[i] = Color.Lerp(paper, graphite, ink * fade);
                }
            var sketch = new Texture2D(width, height, TextureFormat.RGB24, false);
            sketch.SetPixels(outPx); sketch.Apply();
            return sketch;
        }

        // The Episode 6 photograph is kept for the walk home and the dream (per profile, outside the build).
        static string GroupPhotoPath => Path.Combine(Application.persistentDataPath, Mindscape.Data.MindscapeDatabase.ProfileKey("group-photo").Replace(':', '_').Replace('/', '_') + ".png");

        public static void SaveGroupPhoto(Texture2D photo)
        {
            try { File.WriteAllBytes(GroupPhotoPath, photo.EncodeToPNG()); }
            catch (System.Exception e) { Debug.LogWarning("Could not keep the group photograph: " + e.Message); }
        }

        public static Texture2D LoadGroupPhoto()
        {
            try
            {
                if (!File.Exists(GroupPhotoPath)) return null;
                var t = new Texture2D(2, 2, TextureFormat.RGB24, false);
                return t.LoadImage(File.ReadAllBytes(GroupPhotoPath)) ? t : null;
            }
            catch { return null; }
        }

        public static void SetLayer(GameObject go, int layer)
        {
            foreach (var t in go.GetComponentsInChildren<Transform>(true)) t.gameObject.layer = layer;
        }
    }

    // A framed memory that is dark until Show lights it up.
    public sealed class MemoryFrame : MonoBehaviour
    {
        Material picture, border; TextMeshPro caption; Light glow;
        float shown, target, speed = 1;
        Color pictureColor = Color.white, borderColor;

        public bool IsShown => target > 0;

        public void Init(Material picture, Material border, TextMeshPro caption, Light glow)
        {
            this.picture = picture; this.border = border; this.caption = caption; this.glow = glow;
            borderColor = border.GetColor("_BaseColor");
            Apply();
        }

        public void Show(float seconds = 1.6f) { target = 1; speed = 1 / Mathf.Max(.05f, seconds); }
        public void Hide(float seconds = 1f) { target = 0; speed = 1 / Mathf.Max(.05f, seconds); }

        void Update()
        {
            if (Mathf.Approximately(shown, target)) return;
            shown = Mathf.MoveTowards(shown, target, speed * Time.deltaTime);
            Apply();
        }

        void Apply()
        {
            float k = Mathf.SmoothStep(0, 1, shown);
            picture.SetColor("_BaseColor", pictureColor * k); picture.color = pictureColor * k;
            border.SetColor("_BaseColor", borderColor * k); border.color = borderColor * k;
            if (caption != null) { var c = caption.color; c.a = k; caption.color = c; }
            if (glow != null) glow.intensity = 1.6f * k;
            transform.localScale = Vector3.one * Mathf.Lerp(.85f, 1, k);
        }
    }

    // Episode 8's dream: where it starts, the far light, and the frames along the way.
    public sealed class DreamSpace : MonoBehaviour
    {
        public Transform start, end;
        public float length;
        public Light doorwayLight;
        public MemoryFrame[] frames;
    }

    // Episode 5's little park: the fountain's middle, where Joey stands, and Justin's way in along the path.
    public sealed class ParkSpace : MonoBehaviour
    {
        public Vector3 fountain, joey, justinFrom, justinTo;
    }
}
