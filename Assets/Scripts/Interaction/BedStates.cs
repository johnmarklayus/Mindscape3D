using UnityEngine;

namespace Mindscape
{
    /// <summary>
    /// Joey's bed and its three looks (model: Assets/Models/Bed/Joey Bed.fbx, made in
    /// Blender/Blend Files/Boy_Sleeping_In_Bed.blend, placed in every house scene by Mindscape > House > Install Joey Bed):
    ///   1. sleeping: the player's character (boy or girl, whichever they chose) asleep under the blanket;
    ///   2. messy: the blanket thrown back, pillow askew, a notebook on the sheet (Ch1 Ep1 before "Make your bed");
    ///   3. neat: blanket pulled up and folded, pillow straight.
    /// The episodes switch <see cref="messy"/> and <see cref="neat"/> on and off themselves (their messyBed / fixedBed
    /// point here); AcademicEpisode.LieInBed calls <see cref="Sleep"/> and GetUp calls <see cref="Wake"/>.
    /// </summary>
    public class BedStates : MonoBehaviour
    {
        [Tooltip("The mattress: its bounds and collider are where the story lays the player down.")]
        public Renderer mattress;
        [Tooltip("The bed frame (wider than the mattress): where the player stands up again is measured from it.")]
        public Renderer frame;
        public GameObject sleepingBoy, sleepingGirl, messy, neat;

        Renderer[] playerBody;
        bool[] playerBodyWas;

        public bool Sleeping => (sleepingBoy != null && sleepingBoy.activeSelf) || (sleepingGirl != null && sleepingGirl.activeSelf);

        public static BedStates InScene() => FindAnyObjectByType<BedStates>();

        /// <summary>Shows the chosen character asleep in the bed and hides the player's own body (still lying there).</summary>
        public void Sleep(Transform player)
        {
            bool girl = PlayerAppearance.IsGirl;
            if (sleepingBoy != null) sleepingBoy.SetActive(!girl);
            if (sleepingGirl != null) sleepingGirl.SetActive(girl);
            if (messy != null) messy.SetActive(false);
            if (neat != null) neat.SetActive(false);
            if (player == null || playerBody != null) return;
            playerBody = player.GetComponentsInChildren<Renderer>();
            playerBodyWas = new bool[playerBody.Length];
            for (int i = 0; i < playerBody.Length; i++) { playerBodyWas[i] = playerBody[i].enabled; playerBody[i].enabled = false; }
        }

        /// <summary>The middle of the mattress top (where a shot of the bed should look).</summary>
        public Vector3 Top
        {
            get
            {
                if (mattress == null) return transform.position;
                var b = mattress.bounds; return new Vector3(b.center.x, b.max.y, b.center.z);
            }
        }

        /// <summary>
        /// The sleeping character's face (only while <see cref="Sleeping"/>): the head is the end of the body toward
        /// <paramref name="head"/> (the head of the bed), the face its top.
        /// </summary>
        public bool Face(Vector3 head, out Vector3 face)
        {
            face = Top;
            var group = sleepingBoy != null && sleepingBoy.activeSelf ? sleepingBoy : sleepingGirl != null && sleepingGirl.activeSelf ? sleepingGirl : null;
            if (group == null) return false;
            bool any = false; var b = new Bounds();
            foreach (var r in group.GetComponentsInChildren<Renderer>())
            {
                if (r.name.Contains("Blanket") || r.name.Contains("Pillow")) continue;
                if (!any) { b = r.bounds; any = true; } else b.Encapsulate(r.bounds);
            }
            if (!any) return false;
            head = Vector3.ProjectOnPlane(head, Vector3.up).normalized;
            float reach = Mathf.Abs(Vector3.Dot(b.extents, new Vector3(Mathf.Abs(head.x), 0, Mathf.Abs(head.z))));
            Vector3 headCentre = b.center + head * (reach * .65f);   // the middle of the big cartoon head, near that end
            face = new Vector3(headCentre.x, b.max.y - .1f, headCentre.z);
            return true;
        }

        /// <summary>The player got up: the bed is left messy and the player's body shows again.</summary>
        public void Wake()
        {
            if (sleepingBoy != null) sleepingBoy.SetActive(false);
            if (sleepingGirl != null) sleepingGirl.SetActive(false);
            if (neat != null) neat.SetActive(false);
            if (messy != null) messy.SetActive(true);
            if (playerBody == null) return;
            for (int i = 0; i < playerBody.Length; i++) if (playerBody[i] != null) playerBody[i].enabled = playerBodyWas[i];
            playerBody = null; playerBodyWas = null;
        }
    }
}
