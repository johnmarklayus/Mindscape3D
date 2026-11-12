using System.Collections.Generic;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.InputSystem;

// Ground movement, a free orbit camera (a full 360° around the player; the player turns to face the way they walk),
// cursor locking, and the crosshair.
// Input comes from PlayerInputBindings; whether an tasks/pause panel is
// blocking control comes from PlayerControls.IsOverlayOpen() on the same GameObject.
// The camera half of this component (orbit, zoom, first person, wall collision) is in
// Assets/Scripts/Camera/PlayerMovement.Camera.cs; its Inspector settings are the "Camera" and "Zoom" fields below.
[RequireComponent(typeof(CharacterController))]
[RequireComponent(typeof(PlayerInputBindings))]
public partial class PlayerMovement : MonoBehaviour
{
    [Header("Movement")]
    public float moveSpeed = 5f;
    public float rotationSpeed = 12f;
    public float gravity = -20f;

    [Header("Animation")]
    public Animator animator;
    public float runSpeed = 8f;
    [Tooltip("Off: Shift does nothing, the player only walks (a story can switch this, e.g. Chapter 3 Episode 8).")]
    public bool canRun = true;

    [Header("Camera")]
    public Transform cameraTransform;
    public Vector3 cameraOffset = new Vector3(0f, 0.45f, -3.5f);
    public float cameraFollowSpeed = 10f;
    public float mouseSensitivity = 0.12f;
    [Tooltip("Degrees per second when turning the camera with the arrow keys or a gamepad stick.")]
    public float keyLookSpeed = 120f;
    [Tooltip("Degrees per second at full tilt of the on-screen look stick (mobile controls).")]
    public float touchLookSpeed = 150f;
    [Tooltip("Degrees per unit of horizontal two-finger swipe (trackpad) or tilt-wheel.")]
    public float scrollTurnSpeed = 0.5f;
    [Tooltip("Zoom per unit of vertical two-finger swipe (trackpad) or mouse wheel.")]
    public float scrollZoomSpeed = 0.02f;
    [Tooltip("Height above the feet the orbit camera looks at: the shoulders, so the camera sits a little above the head.")]
    public float cameraTargetHeight = 2.1f;
    public float cameraShoulderOffset = 0.55f;
    [Tooltip("How far below / above the player the orbit camera can swing, in degrees.")]
    public float orbitPitchMin = -10f;
    public float orbitPitchMax = 80f;
    // Looking up further than this drops the camera below the player's head and fills the screen with sky.
    const float LowestPitch = -10f;
    const float FirstPersonPitchUp = 80f;
    const float MinSkinWidth = 0.08f;
    const float MinStepOffset = 0.5f;
    [Tooltip("Degrees per pixel when dragging a finger on open screen (mobile controls).")]
    public float touchDragSpeed = 0.18f;
    public float cameraCollisionRadius = 0.25f;
    public float cameraCollisionPadding = 0.15f;
    public LayerMask cameraCollisionMask = ~0;
    [Tooltip("Turning the camera stops when a wall would pull it closer than this to the player (it bumps into the wall instead of swinging through it into the character).")]
    public float cameraWallStopDistance = 1.5f;

    [Header("Zoom")]
    public float zoomSpeed = 5f;
    public float minDistance = 2.5f;
    public float maxDistance = 10f;
    [Tooltip("Scrolling in past the closest third-person distance switches to first person; scrolling out switches back.")]
    public bool allowFirstPerson = true;
    [Tooltip("How fast the camera glides between third and first person.")]
    public float viewSwitchSpeed = 8f;
    [Tooltip("Eye height above the feet in first person. 0 measures the character model (a little below the top of the head); the third-person orbit looks at the shoulders instead.")]
    public float firstPersonEyeHeight = 0f;

    [Header("Crosshair")]
    public bool showCrosshair = true;
    public float crosshairSize = 6f;
    public Color crosshairColor = Color.white;

    // Saved view choice (Settings > Mobile controls > First-person view, the on-screen View button, or scrolling): the
    // next scene starts in the same view.
    public const string FirstPersonKey = "Mindscape.FirstPerson";

    private PlayerInputBindings _input;
    private PlayerControls _hud;
    private CharacterController _controller;
    private bool _snapCamera;
    private bool _cameraBlocked;   // this frame's camera was pulled in by a wall
    private Vector3 _verticalVelocity;
    private float _yaw;
    private float _pitch = 15f;
    private bool _recapture = true;
    private bool _firstPerson;
    private float _viewBlend;   // 0 = third person, 1 = first person
    private float _eyeHeight;
    private UnityEngine.UIElements.VisualElement _crosshair;   // the dot (Crosshair.uxml), drawn by UI Toolkit

    void Awake()
    {
        _controller = GetComponent<CharacterController>();
        _input = GetComponent<PlayerInputBindings>();
        _hud = GetComponent<PlayerControls>();

        if (animator == null)
            animator = GetComponentInChildren<Animator>();
        if (animator != null)
            animator.applyRootMotion = false;
        else
            Debug.LogWarning("PlayerMovement needs an Animator on the player or a child model.", this);

        if (cameraTransform == null && Camera.main != null)
            cameraTransform = Camera.main.transform;

        if (cameraTransform != null)
            _yaw = transform.eulerAngles.y;

        // Scenes saved with the old controller (skin 0.02, step 0.3) snag on wall edges and kerbs. A wider skin keeps the
        // capsule from wedging into corners, and a taller step lets it climb kerbs and thresholds.
        _controller.skinWidth = Mathf.Max(_controller.skinWidth, MinSkinWidth);
        _controller.stepOffset = Mathf.Max(_controller.stepOffset, MinStepOffset);
        FitCapsuleToModel();

        orbitPitchMin = Mathf.Max(orbitPitchMin, LowestPitch);   // scenes saved with the old, lower limit
        _pitch = Mathf.Clamp(_pitch, orbitPitchMin, orbitPitchMax);
        if (allowFirstPerson && PlayerPrefs.GetInt(FirstPersonKey, 0) == 1) { _firstPerson = true; _viewBlend = 1f; }
        _eyeHeight = MeasureEyeHeight();
        BuildCrosshair();
    }

    // Scenes were saved with a 3.5-tall capsule round a 2.54-tall character: taller than the school's doorways (4.4 at 2x), so the
    // player could not walk through doors the character fits through. The capsule is fitted to the model, with a little headroom.
    void FitCapsuleToModel()
    {
        var mesh = animator != null ? animator.GetComponentInChildren<SkinnedMeshRenderer>() : GetComponentInChildren<SkinnedMeshRenderer>();
        if (mesh == null) return;
        float model = (mesh.bounds.max.y - transform.position.y) / Mathf.Max(0.0001f, transform.lossyScale.y);   // local units, feet at 0
        if (model < 0.5f || _controller.height <= model * 1.08f) return;
        _controller.height = Mathf.Max(model * 1.05f, _controller.radius * 2f);
        _controller.center = new Vector3(_controller.center.x, _controller.height * .5f, _controller.center.z);
    }

    void Update()
    {
        if (EpisodeLoadingScreen.IsActive) return;
        UpdateCrosshair();
        HandleCursor();

        if (IsOverlayOpen())
        {
            if (animator != null)
                animator.SetFloat("Speed", 0f);
            return;
        }

        HandleMovement();
    }

    void LateUpdate()
    {
        if (EpisodeLoadingScreen.IsActive) return;
        if (IsOverlayOpen())
            return;

        HandleCamera();
    }

    bool IsOverlayOpen() => _hud != null && _hud.IsOverlayOpen();

    void HandleMovement()
    {
        // The Move action is a 2D composite: x = right-left, y = up-down (see GameControls.inputactions).
        // With the mobile controls on, only the on-screen stick moves the player (no WASD / gamepad), and the other way round.
        bool mobile = MobileControls.Enabled;
        Vector2 moveInput = !mobile && _input.Move != null ? _input.Move.ReadValue<Vector2>() : Vector2.zero;
        if (mobile) moveInput += MobileInput.MoveAxis;
        if (moveInput.sqrMagnitude > 1f) moveInput.Normalize();
        Vector3 input = new Vector3(moveInput.x, 0f, moveInput.y).normalized;

        Quaternion yawRotation = Quaternion.Euler(0f, _yaw, 0f);
        Vector3 forward = yawRotation * Vector3.forward;
        Vector3 right = yawRotation * Vector3.right;

        Vector3 moveDir = forward * input.z + right * input.x;

        bool moving = moveDir.sqrMagnitude > 0.01f;
        bool running = canRun && moving && !mobile && _input.Run != null && _input.Run.IsPressed();

        // The camera orbits freely; the player turns toward where they are walking.
        if (moving)
            transform.rotation = Quaternion.Slerp(transform.rotation, Quaternion.LookRotation(moveDir), rotationSpeed * Time.deltaTime);

        float speed = running ? runSpeed : moveSpeed;

        if (animator != null)
            animator.SetFloat("Speed", moving ? (running ? 2f : 1f) : 0f);

        // Keep a small downward velocity while grounded rather than resetting to 0,
        // so isGrounded stays true on slopes and steps instead of flickering.
        if (_controller.isGrounded && _verticalVelocity.y < 0f)
            _verticalVelocity.y = -2f;

        _verticalVelocity.y += gravity * Time.deltaTime;

        // One Move for walking and falling together: two separate calls make the controller stop dead against a wall or
        // kerb (the sideways Move is blocked, then the vertical one has nothing to slide along) instead of sliding past it.
        Vector3 before = transform.position;
        _controller.Move((moveDir * speed + _verticalVelocity) * Time.deltaTime);
        CheckStuck(moving, moveDir, speed, before);
    }

    // The last surface the controller pressed against while walking, for the unstick fallback below.
    Vector3 _contactNormal;
    float _contactTime = -10f;
    float _stuckFor;

    void OnControllerColliderHit(ControllerColliderHit hit)
    {
        if (hit.normal.y > 0.7f) return;   // the floor
        _contactNormal = hit.normal;
        _contactTime = Time.time;
        _contactName = hit.collider != null ? hit.collider.name : null;
    }
    string _contactName;

    // Safety net: walking was asked for but the player has not moved for a moment. Nudge them out along the surface they
    // are pressing into, so a snagged corner, wedge or kerb never holds them for good. Walking straight into a wall is
    // not a snag (the player simply walks away), so a head-on contact is left alone.
    void CheckStuck(bool moving, Vector3 moveDir, float speed, Vector3 before)
    {
        Vector3 moved = transform.position - before; moved.y = 0f;
        float wanted = speed * Time.deltaTime;
        if (!moving || moved.magnitude > wanted * 0.1f) { _stuckFor = 0f; return; }

        _stuckFor += Time.deltaTime;
        if (_stuckFor < StuckSeconds) return;
        _stuckFor = 0f;

        Vector3 normal = Time.time - _contactTime < 0.5f ? Vector3.ProjectOnPlane(_contactNormal, Vector3.up) : -moveDir;
        if (normal.sqrMagnitude < 0.0001f) normal = -moveDir;
        // Head-on into a flat wall: not trapped, nothing to fix.
        if (Vector3.Dot(normal.normalized, -moveDir.normalized) > 0.95f) return;

        Debug.LogWarning($"Player snagged on '{_contactName}'; nudging out along {normal.normalized}.", this);
        _controller.Move(normal.normalized * UnstickDistance + Vector3.up * 0.05f);
    }

    const float StuckSeconds = 1f;
    const float UnstickDistance = 0.25f;

    void HandleCursor()
    {
        if (Mouse.current == null) return;

        // The mobile controls are pressed with the pointer, so it is never captured while they are on.
        if (MobileControls.Enabled)
        {
            if (Cursor.lockState != CursorLockMode.None) Cursor.lockState = CursorLockMode.None;
            Cursor.visible = true;
            return;
        }

        if (IsOverlayOpen())
        {
            Cursor.lockState = CursorLockMode.None;
            Cursor.visible = true;
            _recapture = true;
            return;
        }

        // Capture when control comes back (start, after a conversation or menu), or after a click if something
        // else released it (Esc in the editor, the browser). Not every frame, so the editor's Esc still frees the mouse.
        bool clicked = Mouse.current.leftButton.wasPressedThisFrame || Mouse.current.rightButton.wasPressedThisFrame;
        if (_recapture || clicked)
        {
            Cursor.lockState = CursorLockMode.Locked;
            Cursor.visible = false;
            _recapture = false;
        }
    }

    void OnEnable() { _recapture = true; UpdateCrosshair(); }

    // The crosshair is a small UI Toolkit element (Assets/UI Toolkit/Crosshair.uxml); showCrosshair, crosshairSize and
    // crosshairColor on this component still control it.
    void BuildCrosshair()
    {
        var ui = Mindscape.AcademicPressure.EpisodeUI.Load();
        var document = Mindscape.AcademicPressure.EpisodeUI.Spawn("Crosshair", ui != null ? ui.crosshair : null, 0, transform);
        if (document == null) return;
        _crosshair = UnityEngine.UIElements.UQueryExtensions.Q(document.rootVisualElement, "crosshair");
        float size = Mathf.Max(1f, crosshairSize);
        _crosshair.style.width = size; _crosshair.style.height = size;
        _crosshair.style.marginLeft = -size * 0.5f; _crosshair.style.marginTop = -size * 0.5f;
        _crosshair.style.backgroundColor = crosshairColor;
    }

    // The story locks the player by disabling this component (dialogue, journal, minigames, pause), and the dot goes with it.
    void OnDisable()
    {
        if (_crosshair != null) _crosshair.style.display = UnityEngine.UIElements.DisplayStyle.None;
    }

    void UpdateCrosshair()
    {
        if (_crosshair == null) return;
        _crosshair.style.display = showCrosshair && !IsOverlayOpen() ? UnityEngine.UIElements.DisplayStyle.Flex : UnityEngine.UIElements.DisplayStyle.None;
    }
}
