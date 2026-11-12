using System.Collections.Generic;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.InputSystem;

// The player's follow camera: the free orbit around the player, mouse / keys / touch look, zoom, the switch to first person,
// and the camera bumping into walls instead of passing through them (or through the player).
// This is the same PlayerMovement component as Assets/Scripts/Player/PlayerMovement.cs (a partial class split over two
// files), so there is nothing extra to add to the player: its settings are the "Camera" and "Zoom" fields on PlayerMovement
// in the Inspector. Story shots and conversations move the camera themselves (AcademicEpisode.Shot, NPCInteractionManager);
// ShotFocus.cs, next to this file, hides the player's body when it blocks one of those shots.
public partial class PlayerMovement
{
    // The orbit camera aims at cameraTargetHeight, the shoulders, and the shoulder offset keeps the head out of the way. First person
    // wants the eyes, so it is measured from the model's own height (a little below the top of the head).
    float MeasureEyeHeight()
    {
        if (firstPersonEyeHeight > 0f) return firstPersonEyeHeight;
        var mesh = animator != null ? animator.GetComponentInChildren<SkinnedMeshRenderer>() : null;
        float top = mesh != null ? mesh.bounds.max.y - transform.position.y : 0f;
        return top > 0.5f ? top * 0.93f : cameraTargetHeight * 0.7f;
    }

    void SetFirstPerson(bool on)
    {
        if (_firstPerson == on) return;
        _firstPerson = on;
        PlayerPrefs.SetInt(FirstPersonKey, on ? 1 : 0);
        PlayerPrefs.Save();
    }

    // Cinematic transitions can reposition the player without retaining the previous camera yaw. The camera then
    // cuts to its place behind the player instead of easing over from the old spot (through walls and doors).
    public void ResetView(float yaw, float pitch = 15f)
    {
        _yaw = yaw;
        _pitch = Mathf.Clamp(pitch, orbitPitchMin, orbitPitchMax);
        _verticalVelocity = Vector3.zero;
        _snapCamera = true;
    }

    void HandleCamera()
    {
        if (cameraTransform == null) return;

        Vector2 look = ReadLook();
        float oldYaw = _yaw, oldPitch = _pitch;
        _yaw = Mathf.Repeat(_yaw + look.x, 360f);
        _pitch -= look.y;
        // In first person you can look right up at the sky; the orbit camera can't swing that low.
        _pitch = Mathf.Clamp(_pitch, _firstPerson ? -FirstPersonPitchUp : orbitPitchMin, orbitPitchMax);
        if (!_firstPerson && !_snapCamera) BumpIntoWalls(oldYaw, oldPitch);

        float zoom = 0f;
        if (!MobileControls.Enabled)
        {
            if (_input.ZoomIn != null && _input.ZoomIn.IsPressed()) zoom += zoomSpeed * Time.deltaTime;
            if (_input.ZoomOut != null && _input.ZoomOut.IsPressed()) zoom -= zoomSpeed * Time.deltaTime;
            // Two-finger swipe up / down on a trackpad (or a mouse wheel) zooms.
            if (Mouse.current != null && Application.isFocused)
                zoom += Mouse.current.scroll.ReadValue().y * scrollZoomSpeed;
        }

        bool viewButton = MobileInput.ConsumeViewToggle();   // the on-screen View button (mobile controls)
        if (_firstPerson)
        {
            if (zoom < -0.0001f || viewButton) { SetFirstPerson(false); cameraOffset.z = -minDistance; _pitch = Mathf.Max(_pitch, orbitPitchMin); }   // scroll out: back to third person
        }
        else
        {
            cameraOffset.z += zoom;
            if (allowFirstPerson && ((cameraOffset.z > -minDistance + 0.0001f && zoom > 0f) || viewButton)) SetFirstPerson(true);   // scroll in past the closest distance
            cameraOffset.z = Mathf.Clamp(cameraOffset.z, -maxDistance, -minDistance);
        }
        ShotFocus.FirstPerson = _firstPerson;

        _viewBlend = _snapCamera ? (_firstPerson ? 1f : 0f) : Mathf.MoveTowards(_viewBlend, _firstPerson ? 1f : 0f, viewSwitchSpeed * Time.deltaTime);

        Quaternion rotation = Quaternion.Euler(_pitch, _yaw, 0f);
        Vector3 targetPos = transform.position + Vector3.up * cameraTargetHeight;
        Vector3 shoulderOffset = rotation * Vector3.right * cameraShoulderOffset;
        Vector3 desiredPos = targetPos + shoulderOffset + rotation * cameraOffset;
        desiredPos = ResolveCameraCollision(targetPos, desiredPos);
        Vector3 eyePos = transform.position + Vector3.up * (firstPersonEyeHeight > 0f ? firstPersonEyeHeight : _eyeHeight);

        // First person: the camera sits at the eyes and looks straight along the view direction, and the body turns with it.
        if (_firstPerson && _viewBlend >= 1f)
        {
            cameraTransform.position = eyePos;
            cameraTransform.rotation = rotation;
            transform.rotation = Quaternion.Euler(0f, _yaw, 0f);
            _snapCamera = false;
            return;
        }

        // Easing out is smooth, but a wall pulls the camera in at once: easing in would leave it inside the wall for a moment.
        Vector3 thirdPos = _snapCamera ? desiredPos : Vector3.Lerp(cameraTransform.position, desiredPos, cameraFollowSpeed * Time.deltaTime);
        if (_cameraBlocked && (thirdPos - targetPos).sqrMagnitude > (desiredPos - targetPos).sqrMagnitude) thirdPos = desiredPos;
        float t = Mathf.SmoothStep(0f, 1f, _viewBlend);
        cameraTransform.position = Vector3.Lerp(thirdPos, eyePos, t);
        Quaternion lookRotation = Quaternion.LookRotation(targetPos - cameraTransform.position + rotation * Vector3.forward * 0.0001f);
        cameraTransform.rotation = t > 0f ? Quaternion.Slerp(lookRotation, rotation, t) : lookRotation;
        _snapCamera = false;
    }

    // Camera turn for this frame, in degrees. Pointer movement (trackpad or mouse, through the Look action) turns
    // the view whenever the game window has focus, captured cursor or not, so losing the capture (Esc, switching
    // windows) never freezes the camera. A two-finger swipe left / right turns it too. Arrow keys and a gamepad
    // stick turn at a steady rate. If the actions read nothing (map disabled by a rebind), the devices are read directly.
    // With the mobile controls on, the on-screen look stick turns the view instead of touches: the Look action's
    // <Pointer>/delta also follows a finger, so dragging the move stick or tapping a button would swing the camera.
    Vector2 ReadLook()
    {
        var mouse = Mouse.current; var keyboard = Keyboard.current;
        // The mobile controls are the only controls while they are on: the view turns by dragging on open screen (a
        // finger, or the mouse held down on a laptop), never by moving the mouse, the arrow keys or a gamepad stick.
        if (MobileControls.Enabled) return TouchDragLook();
        Vector2 pointer = _input.Look != null ? _input.Look.ReadValue<Vector2>() : Vector2.zero;
        if (pointer == Vector2.zero && mouse != null) pointer = mouse.delta.ReadValue();
        bool active = Application.isFocused || Cursor.lockState == CursorLockMode.Locked;
        Vector2 look = active ? pointer * mouseSensitivity : Vector2.zero;
        if (active && mouse != null) look.x += mouse.scroll.ReadValue().x * scrollTurnSpeed;

        Vector2 keys = _input.LookKeys != null ? _input.LookKeys.ReadValue<Vector2>() : Vector2.zero;
        if (keys == Vector2.zero && keyboard != null)
            keys = new Vector2((keyboard.rightArrowKey.isPressed ? 1 : 0) - (keyboard.leftArrowKey.isPressed ? 1 : 0),
                               (keyboard.upArrowKey.isPressed ? 1 : 0) - (keyboard.downArrowKey.isPressed ? 1 : 0));
        return look + keys * keyLookSpeed * Time.deltaTime;
    }

    // Mobile: a finger dragged on open screen orbits the camera, as well as the look stick. Touches that start on a
    // stick or a button belong to that control.
    readonly List<RaycastResult> _uiHits = new List<RaycastResult>();
    readonly Dictionary<int, bool> _touchOnUI = new Dictionary<int, bool>();
    bool _mouseDragOnUI;
    Vector2 TouchDragLook()
    {
        var screen = Touchscreen.current;
        Vector2 drag = Vector2.zero;
        // A laptop with the mobile controls on: holding the mouse button down on open screen drags the view like a finger.
        var mouse = Mouse.current;
        if (mouse != null)
        {
            if (mouse.leftButton.wasPressedThisFrame) _mouseDragOnUI = StartsOnUI(mouse.position.ReadValue());
            if (mouse.leftButton.isPressed && !_mouseDragOnUI && (screen == null || !screen.primaryTouch.press.isPressed))
                drag += mouse.delta.ReadValue();
        }
        if (screen == null) return drag * touchDragSpeed;
        foreach (var touch in screen.touches)
        {
            var phase = touch.phase.ReadValue();
            if (phase == UnityEngine.InputSystem.TouchPhase.None) continue;
            int id = touch.touchId.ReadValue();
            if (phase == UnityEngine.InputSystem.TouchPhase.Began || !_touchOnUI.ContainsKey(id))
                _touchOnUI[id] = StartsOnUI(touch.startPosition.ReadValue());
            if (phase == UnityEngine.InputSystem.TouchPhase.Moved && !_touchOnUI[id])
                drag += touch.delta.ReadValue();
            if (phase == UnityEngine.InputSystem.TouchPhase.Ended || phase == UnityEngine.InputSystem.TouchPhase.Canceled)
                _touchOnUI.Remove(id);
        }
        return drag * touchDragSpeed;
    }

    bool StartsOnUI(Vector2 position)
    {
        if (EventSystem.current == null) return false;
        _uiHits.Clear();
        EventSystem.current.RaycastAll(new PointerEventData(EventSystem.current) { position = position }, _uiHits);
        return _uiHits.Count > 0;
    }

    // The camera is solid: a turn that would swing it into a wall (so the wall pulls it in close to the player, or
    // through them) stops at the wall instead. Yaw and pitch are checked on their own, so the camera still slides along
    // the wall on the other axis, and a turn away from the wall (more room) is always allowed, so it never gets stuck.
    void BumpIntoWalls(float oldYaw, float oldPitch)
    {
        if (Mathf.Approximately(oldYaw, _yaw) && Mathf.Approximately(oldPitch, _pitch)) return;
        float before = CameraRoom(oldYaw, oldPitch);
        if (!Mathf.Approximately(oldYaw, _yaw))
        {
            float room = CameraRoom(_yaw, oldPitch);
            if (room < cameraWallStopDistance && room < before - 0.01f) _yaw = oldYaw;
            else before = room;
        }
        if (!Mathf.Approximately(oldPitch, _pitch))
        {
            float room = CameraRoom(_yaw, _pitch);
            if (room < cameraWallStopDistance && room < before - 0.01f) _pitch = oldPitch;
        }
    }

    // How far from the look-at point the camera could stand at this yaw and pitch before a wall stops it.
    float CameraRoom(float yaw, float pitch)
    {
        Quaternion rotation = Quaternion.Euler(pitch, yaw, 0f);
        Vector3 targetPos = transform.position + Vector3.up * cameraTargetHeight;
        Vector3 toCamera = rotation * Vector3.right * cameraShoulderOffset + rotation * cameraOffset;
        float distance = toCamera.magnitude;
        if (distance <= 0.01f) return distance;
        return ClearDistance(targetPos, toCamera / distance, distance, CameraRadius());
    }

    // Wide enough for the whole near plane, so a wall beside the camera never shows through a corner of the screen.
    float CameraRadius()
    {
        float radius = cameraCollisionRadius;
        var cam = cameraTransform != null ? cameraTransform.GetComponent<Camera>() : null;
        if (cam != null)
        {
            float halfHeight = cam.nearClipPlane * Mathf.Tan(cam.fieldOfView * 0.5f * Mathf.Deg2Rad);
            radius = Mathf.Max(radius, new Vector3(halfHeight * cam.aspect, halfHeight, cam.nearClipPlane).magnitude + 0.02f);
        }
        return radius;
    }

    // Sphere-casts from the player toward the desired camera position and pulls the camera
    // in front of any geometry it would otherwise clip through.
    Vector3 ResolveCameraCollision(Vector3 targetPos, Vector3 desiredPos)
    {
        Vector3 toCamera = desiredPos - targetPos;
        float distance = toCamera.magnitude;
        if (distance <= 0.01f)
            return desiredPos;

        Vector3 direction = toCamera / distance;
        float radius = CameraRadius();
        float nearestDistance = ClearDistance(targetPos, direction, distance, radius);
        _cameraBlocked = nearestDistance < distance;
        Vector3 result = _cameraBlocked ? targetPos + direction * Mathf.Max(0.1f, nearestDistance - cameraCollisionPadding) : desiredPos;
        return KeepOffSideWalls(result, radius);
    }

    // The distance along the line from the player to the camera before anything (not the player) is hit.
    // Back faces count too: some city walls are single-sided and the camera would pass through from behind.
    float ClearDistance(Vector3 targetPos, Vector3 direction, float distance, float radius)
    {
        bool backfaces = Physics.queriesHitBackfaces;
        Physics.queriesHitBackfaces = true;
        RaycastHit[] hits = Physics.SphereCastAll(
            targetPos,
            radius,
            direction,
            distance,
            cameraCollisionMask,
            QueryTriggerInteraction.Ignore);
        // A thin cast as well: the wide one ignores what it already touches at the start (a wall the player leans on).
        RaycastHit[] thin = Physics.SphereCastAll(targetPos, 0.05f, direction, distance, cameraCollisionMask, QueryTriggerInteraction.Ignore);
        Physics.queriesHitBackfaces = backfaces;
        if (thin.Length > 0) { var all = new RaycastHit[hits.Length + thin.Length]; hits.CopyTo(all, 0); thin.CopyTo(all, hits.Length); hits = all; }

        float nearestDistance = distance;
        for (int i = 0; i < hits.Length; i++)
        {
            Transform hitTransform = hits[i].transform;
            if (hitTransform == transform || hitTransform.IsChildOf(transform) || hits[i].distance <= 0f)
                continue;

            if (hits[i].distance < nearestDistance)
                nearestDistance = hits[i].distance;
        }
        return nearestDistance;
    }

    // In a narrow gap (between two houses, along a fence) the line to the player can be clear while a wall runs right
    // beside the camera, so the near plane cut into it and half the screen was wall. Nudge the camera out of any wall
    // closer than the near plane's reach, sideways and up/down.
    Vector3 KeepOffSideWalls(Vector3 position, float radius)
    {
        bool backfaces = Physics.queriesHitBackfaces;
        Physics.queriesHitBackfaces = true;
        Vector3 forward = cameraTransform != null ? cameraTransform.forward : transform.forward;
        Vector3 right = Vector3.Cross(Vector3.up, forward).normalized;
        if (right.sqrMagnitude < 0.01f) right = transform.right;
        position = Nudge(position, right, radius);
        position = Nudge(position, -right, radius);
        position = Nudge(position, Vector3.up, radius);
        position = Nudge(position, Vector3.down, radius);
        Physics.queriesHitBackfaces = backfaces;
        return position;
    }

    Vector3 Nudge(Vector3 position, Vector3 dir, float radius)
    {
        if (!Physics.Raycast(position, dir, out var hit, radius, cameraCollisionMask, QueryTriggerInteraction.Ignore)) return position;
        if (hit.transform == transform || hit.transform.IsChildOf(transform)) return position;
        return position - dir * (radius - hit.distance);
    }
}
