using System.Linq;
using UnityEngine;
using UnityEngine.Rendering;

namespace Mindscape.SocialDynamics
{
    // A real planar mirror: a reflection camera stands where the viewing camera (Camera.main: the follow camera or a
    // story shot) would be if it were mirrored through the glass, and its view is cut to exactly the glass, so what
    // the mirror shows changes as you move and turn, like a mirror. The glass gets its own quad whose corners are the
    // corners of that view. For the ending a second camera can join it: the same view, but it also sees the
    // YoungerLayer (younger Joey standing beside you, invisible to the room's own camera), and the mirror
    // cross-fades between the two pictures (Blend).
    public sealed class SocialMirror : MonoBehaviour
    {
        public const int YoungerLayer = 30;
        public Transform player;
        Renderer[] body;
        ShadowCastingMode[] bodyModes;
        public float planeX;
        public float side = -1;        // which way the room is from the mirror, along X (-1: the mirror is on an east wall)
        public float eyeHeight = 2.6f; // unused since the mirror follows the viewing camera (kept for saved scenes)
        public float activeRange = 0;  // > 0: the reflection renders only while the player is this close (scenery mirrors)
        Camera reflection, withYounger;
        RenderTexture texture, youngerTexture;
        Material material;
        bool blendShader;
        float blend, glow = 1;
        Vector3[] corners;             // the glass, world space: lower-left, lower-right, upper-left, upper-right (as the reflection sees it)
        Vector3 normal;                // out of the glass, into the room
        Mesh glass;

        /// <summary>0 shows the plain reflection, 1 the reflection with younger Joey (after ShowYounger).</summary>
        public float Blend
        {
            get => blend;
            set { blend = Mathf.Clamp01(value); if (material != null && blendShader) material.SetFloat("_Blend", blend); }
        }

        /// <summary>Brightens the mirror a little (1 = as it is).</summary>
        public float Glow
        {
            get => glow;
            set { glow = value; if (material != null && blendShader) material.SetFloat("_Glow", glow); }
        }

        void Start()
        {
            gameObject.layer = 2;
            BuildGlass();
            float w = Vector3.Distance(corners[0], corners[1]), h = Vector3.Distance(corners[0], corners[2]);
            texture = NewTexture(w, h);
            var shader = Resources.Load<Shader>("Shaders/MirrorBlend");
            blendShader = shader != null && shader.isSupported;
            if (blendShader)
            {
                material = new Material(shader);
                material.SetTexture("_MainTex", texture);
                material.SetTexture("_SecondTex", texture);
                material.SetFloat("_Blend", blend); material.SetFloat("_Glow", glow);
            }
            else
            {
                material = new Material(Shader.Find("Universal Render Pipeline/Unlit"));
                material.mainTexture = texture;
                material.mainTextureScale = new Vector2(-1, 1); material.mainTextureOffset = new Vector2(1, 0);
            }
            GetComponent<Renderer>().material = material;
            reflection = MakeCamera("Mirror reflection camera", texture, ~((1 << 2) | (1 << YoungerLayer)));
        }

        // Sharp enough to read the face at arm's length; the long side 1024, the other side by the glass's shape.
        static RenderTexture NewTexture(float w, float h)
        {
            float k = 1024f / Mathf.Max(.01f, Mathf.Max(w, h));
            var t = new RenderTexture(Mathf.Max(128, Mathf.RoundToInt(w * k)), Mathf.Max(128, Mathf.RoundToInt(h * k)), 24);
            t.antiAliasing = 2;
            return t;
        }

        // The face of the glass that looks into the room becomes a quad of its own: its corners are the reflection
        // view's corners, so the picture lands on it one to one. (The material's shader swaps left and right, so the
        // U coordinates are given already swapped.)
        void BuildGlass()
        {
            var r = GetComponent<Renderer>();
            Bounds b = r.bounds;
            float s = side >= 0 ? 1 : -1;
            // The glass is thin along X or along Z; `side` says which way along that axis the room is.
            bool alongX = b.size.x <= b.size.z;
            normal = alongX ? new Vector3(s, 0, 0) : new Vector3(0, 0, s);
            Vector3 face = b.center + normal * (alongX ? b.extents.x : b.extents.z);
            // The reflection camera faces into the room (along the normal); its right is up × normal.
            Vector3 right = Vector3.Cross(Vector3.up, normal) * (alongX ? b.extents.z : b.extents.x);
            Vector3 low = Vector3.up * b.extents.y;
            corners = new[] { face - right - low, face + right - low, face - right + low, face + right + low };
            glass = new Mesh { name = "Mirror glass" };
            glass.vertices = corners.Select(c => transform.InverseTransformPoint(c + normal * .002f)).ToArray();
            glass.uv = new[] { new Vector2(1, 0), new Vector2(0, 0), new Vector2(1, 1), new Vector2(0, 1) };
            // Both windings: whichever is the front, the room side shows.
            glass.triangles = new[] { 0, 2, 1, 1, 2, 3, 0, 1, 2, 1, 3, 2 };
            glass.RecalculateNormals(); glass.RecalculateBounds();
            GetComponent<MeshFilter>().sharedMesh = glass;
        }

        Camera MakeCamera(string name, RenderTexture target, int mask)
        {
            var cam = new GameObject(name).AddComponent<Camera>();
            cam.targetTexture = target; cam.cullingMask = mask;
            cam.nearClipPlane = .05f; cam.farClipPlane = 40; cam.fieldOfView = 55;
            cam.clearFlags = CameraClearFlags.SolidColor; cam.backgroundColor = new Color(.18f, .23f, .27f);
            return cam;
        }

        // Mirrors the viewing camera through the glass and cuts its view to the glass: an off-axis frustum whose near
        // plane is the glass itself, so the wall the mirror hangs on (and the room behind it) never shows.
        bool Place(Camera cam, Camera viewer)
        {
            Vector3 eye = viewer.transform.position;
            float d = Vector3.Dot(eye - corners[0], normal);
            if (d < .05f) return false;   // the viewer is behind the mirror
            Vector3 mirrored = eye - 2 * d * normal;
            cam.transform.SetPositionAndRotation(mirrored, Quaternion.LookRotation(normal, Vector3.up));
            Vector3 right = cam.transform.right, up = cam.transform.up;
            float l = Vector3.Dot(corners[0] - mirrored, right), rr = Vector3.Dot(corners[1] - mirrored, right);
            float bt = Vector3.Dot(corners[0] - mirrored, up), tp = Vector3.Dot(corners[2] - mirrored, up);
            cam.nearClipPlane = d;
            cam.farClipPlane = d + 40;
            cam.projectionMatrix = Matrix4x4.Frustum(l, rr, bt, tp, d, d + 40);
            return true;
        }

        /// <summary>Starts the second reflection, which also sees everything on YoungerLayer. Blend fades it in.</summary>
        public void ShowYounger()
        {
            if (withYounger != null || !blendShader) return;
            youngerTexture = NewTexture(texture.width, texture.height);
            withYounger = MakeCamera("Mirror reflection camera (younger)", youngerTexture, ~(1 << 2));
            material.SetTexture("_SecondTex", youngerTexture);
        }

        void OnEnable()
        {
            RenderPipelineManager.beginCameraRendering += BeginCamera;
            RenderPipelineManager.endCameraRendering += EndCamera;
        }
        void OnDisable()
        {
            RenderPipelineManager.beginCameraRendering -= BeginCamera;
            RenderPipelineManager.endCameraRendering -= EndCamera;
        }
        bool Mine(Camera camera) => camera != null && (camera == reflection || camera == withYounger);
        // ShotFocus hides the player's body (shadow only) while a story shot looks at the mirror, so the reflection
        // cameras alone put the body back for their own render.
        void BeginCamera(ScriptableRenderContext context, Camera camera)
        {
            if (!Mine(camera) || player == null) return;
            // Looked up each time: the player's model can change (boy / girl, outfits, the backpack).
            body = player.GetComponentsInChildren<Renderer>(true);
            if (bodyModes == null || bodyModes.Length != body.Length) bodyModes = new ShadowCastingMode[body.Length];
            for (int i = 0; i < body.Length; i++)
            {
                if (body[i] == null) continue;
                bodyModes[i] = body[i].shadowCastingMode;
                if (bodyModes[i] == ShadowCastingMode.ShadowsOnly) body[i].shadowCastingMode = ShadowCastingMode.On;
            }
        }
        void EndCamera(ScriptableRenderContext context, Camera camera)
        {
            if (!Mine(camera) || body == null || bodyModes == null) return;
            for (int i = 0; i < body.Length; i++) if (body[i] != null) body[i].shadowCastingMode = bodyModes[i];
        }
        void LateUpdate()
        {
            if (reflection == null) return;
            var viewer = Camera.main;
            bool on = viewer != null && (activeRange <= 0 || player == null
                || (player.position - transform.position).sqrMagnitude < activeRange * activeRange);
            if (on) on = Place(reflection, viewer);
            if (reflection.enabled != on) reflection.enabled = on;
            if (withYounger != null)
            {
                bool young = on && Place(withYounger, viewer);
                if (withYounger.enabled != young) withYounger.enabled = young;
            }
        }
        void OnDestroy()
        {
            if (reflection != null) Destroy(reflection.gameObject);
            if (withYounger != null) Destroy(withYounger.gameObject);
            if (texture != null) { texture.Release(); Destroy(texture); }
            if (youngerTexture != null) { youngerTexture.Release(); Destroy(youngerTexture); }
            if (material != null) Destroy(material);
            if (glass != null) Destroy(glass);
        }
    }
}
