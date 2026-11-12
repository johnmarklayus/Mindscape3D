using UnityEngine;
using UnityEngine.InputSystem;

// Emergency "unstuck" key: R moves the player to the nearest clear spot of floor (stuck on a bed, wedged in furniture or
// a wall corner). Only while you can walk around (this component is off during story scenes and menus).
public partial class PlayerMovement
{
    float _lastUnstuck = -10f;

    void HandleUnstuck()
    {
        var keyboard = Keyboard.current;
        if (keyboard == null || !keyboard.rKey.wasPressedThisFrame) return;
        if (Time.unscaledTime - _lastUnstuck < .75f) return;
        _lastUnstuck = Time.unscaledTime;
        if (!FindClearFloor(out var spot)) return;
        _controller.enabled = false;
        transform.position = spot + Vector3.up * .05f;
        _controller.enabled = true;
        _verticalVelocity = Vector3.zero;
    }

    // The nearest spot within 8 m where the floor is the room's floor (not a bed or table top) and the body fits.
    bool FindClearFloor(out Vector3 spot)
    {
        spot = transform.position;
        float height = _controller.height * transform.lossyScale.y, radius = _controller.radius * transform.lossyScale.x;
        Vector3 here = transform.position;
        float from = here.y + height * .9f;   // under the ceiling, above furniture tops
        const int angles = 16;
        bool wasEnabled = _controller.enabled;
        _controller.enabled = false;   // keep our own capsule out of the checks
        try
        {
            // The floor level here: the lowest walkable surface around (the room floor, not the bed you are standing on).
            float floor = float.MaxValue;
            for (float d = .6f; d <= 4f; d += .6f)
                for (int a = 0; a < angles; a++)
                    if (Ground(Around(here, d, a, angles), from, here.y - 3f, out var g)) floor = Mathf.Min(floor, g.y);
            if (floor == float.MaxValue) return false;

            for (float d = .4f; d <= 8f; d += .4f)
            {
                float best = float.MaxValue; Vector3 found = Vector3.zero;
                for (int a = 0; a < angles; a++)
                {
                    if (!Ground(Around(here, d, a, angles), from, here.y - 3f, out var g)) continue;
                    if (g.y > floor + .3f) continue;   // a table, the bed, a step up onto furniture
                    var bottom = g + Vector3.up * (radius + .08f); var top = g + Vector3.up * Mathf.Max(radius + .08f, height - radius);
                    if (Physics.CheckCapsule(bottom, top, radius * 1.05f, ~0, QueryTriggerInteraction.Ignore)) continue;
                    float score = (g - here).sqrMagnitude;
                    if (score < best) { best = score; found = g; }
                }
                if (best < float.MaxValue) { spot = found; return true; }
            }
            return false;
        }
        finally { _controller.enabled = wasEnabled; }
    }

    static Vector3 Around(Vector3 centre, float distance, int index, int count)
    {
        float angle = index * Mathf.PI * 2f / count;
        return centre + new Vector3(Mathf.Cos(angle), 0, Mathf.Sin(angle)) * distance;
    }

    // The walkable surface under a point: the highest upward-facing hit between the start height and the lowest allowed.
    static bool Ground(Vector3 at, float fromY, float lowestY, out Vector3 ground)
    {
        ground = Vector3.zero;
        var start = new Vector3(at.x, fromY, at.z);
        if (!Physics.Raycast(start, Vector3.down, out var hit, fromY - lowestY, ~0, QueryTriggerInteraction.Ignore)) return false;
        if (hit.normal.y < .75f) return false;
        ground = hit.point;
        return true;
    }
}
