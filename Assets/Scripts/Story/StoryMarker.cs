using System.Collections.Generic;
using UnityEngine;

namespace Mindscape.AcademicPressure
{
    public enum StoryMarkerKind { Person, Seat, Camera, Spot }

    /// <summary>
    /// A place in the scene that an episode uses instead of a position worked out in code: where someone stands, where
    /// Joey sits, where the story camera goes. The episode looks a marker up by its <see cref="id"/>; with no marker of
    /// that id in the scene, the episode uses its built-in position. Drag the marker in the Scene view to move the
    /// thing it places: its position is the spot (for a seat: the top of the cushion) and its blue arrow (forward) is
    /// the way the person faces or the camera looks.
    /// The episode's Inspector lists every id it reads and can create the missing markers at the built-in positions.
    /// </summary>
    [AddComponentMenu("Mindscape/Story Marker")]
    [DisallowMultipleComponent]
    public sealed class StoryMarker : MonoBehaviour
    {
        [Tooltip("The name the episode looks for, for example \"Family/Mom\". The episode's Inspector lists the names it uses.")]
        public string id;
        public StoryMarkerKind kind = StoryMarkerKind.Person;
        [Tooltip("What this marker places (shown in the Inspector only).")]
        [TextArea(1, 3)] public string note;

        /// <summary>The active marker with this id in the loaded scenes, or null.</summary>
        public static StoryMarker Find(string id)
        {
            if (string.IsNullOrEmpty(id)) return null;
            foreach (var m in FindObjectsByType<StoryMarker>(FindObjectsInactive.Exclude, FindObjectsSortMode.None))
                if (m.id == id && m.isActiveAndEnabled) return m;
            return null;
        }

        public static readonly Dictionary<StoryMarkerKind, Color> Colors = new Dictionary<StoryMarkerKind, Color>
        {
            { StoryMarkerKind.Person, new Color(1f, .62f, .2f) },
            { StoryMarkerKind.Seat, new Color(.35f, .85f, .45f) },
            { StoryMarkerKind.Camera, new Color(.35f, .7f, 1f) },
            { StoryMarkerKind.Spot, new Color(1f, .85f, .3f) },
        };

#if UNITY_EDITOR
        void OnDrawGizmos()
        {
            var c = Colors[kind];
            Gizmos.color = c;
            Vector3 p = transform.position, f = transform.forward;
            switch (kind)
            {
                case StoryMarkerKind.Person:
                    // A standing figure about as tall as the cast (1.7 m), with the way they face.
                    Gizmos.DrawWireSphere(p + Vector3.up * 1.55f, .2f);
                    Gizmos.DrawLine(p, p + Vector3.up * 1.35f);
                    Gizmos.DrawWireSphere(p, .35f);
                    break;
                case StoryMarkerKind.Seat:
                    Gizmos.DrawWireCube(p + Vector3.up * .05f, new Vector3(.5f, .1f, .5f));
                    Gizmos.DrawLine(p, p + Vector3.up * .7f);
                    break;
                case StoryMarkerKind.Camera:
                    Gizmos.matrix = Matrix4x4.TRS(p, transform.rotation, Vector3.one);
                    Gizmos.DrawFrustum(Vector3.zero, 50, 1.2f, .1f, 16f / 9f);
                    Gizmos.matrix = Matrix4x4.identity;
                    break;
                default:
                    Gizmos.DrawWireSphere(p, .4f);
                    break;
            }
            Gizmos.color = new Color(.3f, .55f, 1f);
            Vector3 from = kind == StoryMarkerKind.Camera ? p : p + Vector3.up * .1f;
            Gizmos.DrawLine(from, from + f * .9f);
            Gizmos.DrawLine(from + f * .9f, from + f * .7f + transform.right * .12f);
            Gizmos.DrawLine(from + f * .9f, from + f * .7f - transform.right * .12f);
            UnityEditor.Handles.color = c;
            UnityEditor.Handles.Label(p + Vector3.up * (kind == StoryMarkerKind.Person ? 2f : .9f), string.IsNullOrEmpty(id) ? "(no id)" : id);
        }
#endif
    }

    /// <summary>One marker an episode reads, with where it goes when the scene has no marker for it.</summary>
    public readonly struct StoryMarkerDefault
    {
        public readonly string id, note;
        public readonly StoryMarkerKind kind;
        public readonly Vector3 position;
        public readonly Quaternion rotation;
        public StoryMarkerDefault(string id, StoryMarkerKind kind, Vector3 position, Vector3 forward, string note)
        {
            this.id = id; this.kind = kind; this.position = position; this.note = note;
            forward = kind == StoryMarkerKind.Camera ? forward : Vector3.ProjectOnPlane(forward, Vector3.up);
            rotation = forward.sqrMagnitude > 1e-6f ? Quaternion.LookRotation(forward) : Quaternion.identity;
        }
    }
}
