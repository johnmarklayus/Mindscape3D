using System.Reflection;
using UnityEngine;

/// <summary>
/// Player movement and camera settings shared by several scenes. A scene's Player uses them when its PlayerMovement
/// "Settings" field points to this asset: change a value here and every scene using the asset changes with it.
/// The assets live in Assets/Settings/Player/, one per kind of place (the scale of the cast and rooms differs between
/// the house, the school and the reunion hall). Each field has the same name and meaning as on PlayerMovement.
/// </summary>
[CreateAssetMenu(menuName = "Mindscape/Player Settings", fileName = "Player Settings")]
public class PlayerSettings : ScriptableObject
{
    [Header("Movement")]
    public float moveSpeed = 5f;
    public float rotationSpeed = 12f;
    public float gravity = -20f;
    public float runSpeed = 8f;
    public bool canRun = true;

    [Header("Camera")]
    [Tooltip("Where the camera sits behind the player (x right, y up, z back).")]
    public Vector3 cameraOffset = new Vector3(0f, 0.45f, -3.5f);
    public float cameraFollowSpeed = 10f;
    public float mouseSensitivity = 0.12f;
    public float keyLookSpeed = 120f;
    public float touchLookSpeed = 150f;
    public float scrollTurnSpeed = 0.5f;
    public float scrollZoomSpeed = 0.02f;
    [Tooltip("The height on the player the camera looks at.")]
    public float cameraTargetHeight = 2.1f;
    public float cameraShoulderOffset = 0.55f;
    public float orbitPitchMin = -10f;
    public float orbitPitchMax = 80f;
    public float touchDragSpeed = 0.18f;
    public float cameraCollisionRadius = 0.25f;
    public float cameraCollisionPadding = 0.15f;
    public LayerMask cameraCollisionMask = ~0;
    public float cameraWallStopDistance = 1.5f;

    [Header("Zoom")]
    public float zoomSpeed = 5f;
    public float minDistance = 2.5f;
    public float maxDistance = 10f;
    public bool allowFirstPerson = true;
    public float viewSwitchSpeed = 8f;
    public float firstPersonEyeHeight = 0f;

    [Header("Crosshair")]
    public bool showCrosshair = true;
    public float crosshairSize = 6f;
    public Color crosshairColor = Color.white;

    static FieldInfo[] Fields => typeof(PlayerSettings).GetFields(BindingFlags.Instance | BindingFlags.Public | BindingFlags.DeclaredOnly);

    /// <summary>Copies every setting onto the player (fields with the same name).</summary>
    public void ApplyTo(PlayerMovement movement)
    {
        foreach (var f in Fields)
        {
            var target = typeof(PlayerMovement).GetField(f.Name, BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic);
            if (target != null && target.FieldType == f.FieldType) target.SetValue(movement, f.GetValue(this));
        }
    }

    /// <summary>Takes every setting from a player (used when the assets were first made from the scenes).</summary>
    public void CopyFrom(PlayerMovement movement)
    {
        foreach (var f in Fields)
        {
            var source = typeof(PlayerMovement).GetField(f.Name, BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic);
            if (source != null && source.FieldType == f.FieldType) f.SetValue(this, source.GetValue(movement));
        }
    }

    /// <summary>The names of the settings this asset holds (the PlayerMovement Inspector greys those fields out).</summary>
    public static bool Holds(string fieldName)
    {
        foreach (var f in Fields) if (f.Name == fieldName) return true;
        return false;
    }
}
