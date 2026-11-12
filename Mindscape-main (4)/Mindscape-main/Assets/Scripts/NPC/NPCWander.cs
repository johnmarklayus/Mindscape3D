using System.Collections.Generic;
using UnityEngine;

// Makes an NPC walk between waypoints around the house.
// Waypoints are plain scene objects (see 'NPC Waypoints' in the Hierarchy): move, add or delete them freely.
// The NPC holds still while the player is close enough to talk, and during any conversation. It does not turn to watch the
// player walk past (that felt like being stared at); it only faces them once a conversation starts (NPCInteractionManager).
[DisallowMultipleComponent]
[AddComponentMenu("Mindscape/NPC Wander")]
public class NPCWander : MonoBehaviour
{
    public enum Pattern { Loop, PingPong, Random }

    [Header("Route")]
    [Tooltip("Where to walk, in order. Keep straight lines between neighbouring points clear of walls and furniture.")]
    public List<Transform> waypoints = new List<Transform>();
    [Tooltip("Loop: 1,2,3,1,2,3.  PingPong: 1,2,3,2,1.  Random: any point, but every pair needs a clear line.")]
    public Pattern pattern = Pattern.PingPong;
    [Tooltip("Begin at the first waypoint instead of where the NPC is placed.")]
    public bool snapToStart = false;

    [Header("Movement")]
    [Min(0.1f)] public float walkSpeed = 1.1f;
    [Tooltip("The animator's Speed while moving: 1 walks, 2 runs (with a Walker controller's Idle/Walk/Run blend).")]
    public float moveAnimationSpeed = 1f;
    [Tooltip("Degrees per second.")] public float turnSpeed = 240f;
    [Tooltip("Start walking only once facing within this many degrees of the target.")]
    [Range(1f, 90f)] public float moveAngle = 35f;
    [Tooltip("Seconds to stand still at each waypoint (random between the two).")]
    public Vector2 pauseSeconds = new Vector2(2f, 6f);

    [Header("Around the player")]
    [Tooltip("Stand still while the player is within the NPC's interaction radius, so they are easy to talk to.")]
    public bool pauseWhenPlayerNear = true;

    NPC npc;
    Transform player;
    Animator[] animators;
    bool[] animatorHasSpeed;
    int target = -1, direction = 1;
    float wait;

    void Awake()
    {
        npc = GetComponent<NPC>();
        animators = GetComponentsInChildren<Animator>(true);
        animatorHasSpeed = new bool[animators.Length];
        int speedHash = Animator.StringToHash("Speed");
        for (int i = 0; i < animators.Length; i++)
            foreach (var parameter in animators[i].parameters)
                if (parameter.nameHash == speedHash && parameter.type == AnimatorControllerParameterType.Float)
                    animatorHasSpeed[i] = true;
        // A kinematic body lets the NPC move every frame without rebuilding static physics.
        if (!TryGetComponent<Rigidbody>(out var body)) body = gameObject.AddComponent<Rigidbody>();
        body.isKinematic = true; body.useGravity = false;
    }

    void Start()
    {
        var pc = FindAnyObjectByType<PlayerControls>();
        if (pc != null) player = pc.transform;
        if (waypoints.Count == 0) return;
        if (snapToStart && waypoints[0] != null) transform.position = waypoints[0].position;
        target = ClosestWaypoint();
        wait = Random.Range(pauseSeconds.x, pauseSeconds.y);
    }

    void Update()
    {
        if (waypoints.Count == 0 || target < 0) { SetWalking(false); return; }
        if (NPCInteractionManager.DialogueActive) { SetWalking(false); return; } // the conversation system owns rotation while talking

        if (pauseWhenPlayerNear && npc != null && npc.IsInRange(player))
        {
            SetWalking(false);
            return;
        }
        if (wait > 0f) { SetWalking(false); wait -= Time.deltaTime; return; }

        var goal = waypoints[target];
        if (goal == null) { SetWalking(false); NextTarget(); return; }
        Vector3 to = goal.position - transform.position;
        Vector3 flat = new Vector3(to.x, 0f, to.z);
        if (flat.magnitude < 0.12f)
        {
            SetWalking(false);
            NextTarget();
            wait = Random.Range(pauseSeconds.x, pauseSeconds.y);
            return;
        }
        float angle = TurnToward(flat);
        if (angle <= moveAngle)
        {
            // A wall or furniture across the route (waypoints laid out before the scenery changed): turn back instead of
            // walking through it.
            if (WallAhead(flat.normalized))
            {
                SetWalking(false);
                TurnBack();
                wait = Random.Range(.6f, 1.6f);
                return;
            }
            SetWalking(true);
            transform.position = Vector3.MoveTowards(transform.position, goal.position, walkSpeed * Time.deltaTime);
        }
        else SetWalking(false);
    }

    static readonly float[] ProbeHeights = { .45f, 1.1f };
    static readonly RaycastHit[] probeHits = new RaycastHit[8];

    // Something solid just ahead at knee or chest height (not a person, not a trigger, not this NPC).
    bool WallAhead(Vector3 direction)
    {
        float scale = Mathf.Max(.5f, transform.lossyScale.y);
        float reach = .45f * scale + walkSpeed * Time.deltaTime;
        foreach (float height in ProbeHeights)
        {
            Vector3 from = transform.position + Vector3.up * height * scale;
            int count = Physics.RaycastNonAlloc(from, direction, probeHits, reach, ~0, QueryTriggerInteraction.Ignore);
            for (int h = 0; h < count; h++)
            {
                var hit = probeHits[h];
                var c = hit.collider;
                if (c.transform.IsChildOf(transform) || c.GetComponentInParent<NPC>() != null || c.GetComponentInParent<CharacterController>() != null) continue;
                if (c.attachedRigidbody != null && !c.attachedRigidbody.isKinematic) continue;   // a ball or a box that gets pushed
                if (Vector3.Dot(hit.normal, Vector3.up) > .6f) continue;                        // a slope or a step, not a wall
                return true;
            }
        }
        return false;
    }

    // Back the way it came: the previous waypoint (or any other one for a random route).
    void TurnBack()
    {
        int n = waypoints.Count;
        if (n <= 1) { target = -1; return; }
        if (pattern == Pattern.Random) { NextTarget(); return; }
        direction = -direction;
        int back = target + direction;
        if (pattern == Pattern.Loop) back = (target - 1 + n) % n;
        target = Mathf.Clamp(back, 0, n - 1);
    }

    void OnDisable() => SetWalking(false);

    void SetWalking(bool walking)
    {
        if (animators == null || animatorHasSpeed == null) return;
        float speed = walking ? moveAnimationSpeed : 0f;
        for (int i = 0; i < animators.Length; i++)
            if (animators[i] != null && animatorHasSpeed[i]) animators[i].SetFloat("Speed", speed);
    }

    float TurnToward(Vector3 worldDirection)
    {
        worldDirection.y = 0f;
        if (worldDirection.sqrMagnitude < 0.0001f) return 0f;
        var want = Quaternion.LookRotation(worldDirection.normalized, Vector3.up);
        transform.rotation = Quaternion.RotateTowards(transform.rotation, want, turnSpeed * Time.deltaTime);
        return Quaternion.Angle(transform.rotation, want);
    }

    int ClosestWaypoint()
    {
        int best = 0; float bestD = float.MaxValue;
        for (int i = 0; i < waypoints.Count; i++)
        {
            if (waypoints[i] == null) continue;
            float d = (waypoints[i].position - transform.position).sqrMagnitude;
            if (d < bestD) { bestD = d; best = i; }
        }
        return best;
    }

    void NextTarget()
    {
        int n = waypoints.Count;
        if (n <= 1) return;
        switch (pattern)
        {
            case Pattern.Loop: target = (target + 1) % n; break;
            case Pattern.PingPong:
                if (target + direction >= n || target + direction < 0) direction = -direction;
                target += direction; break;
            default:
                int next; do { next = Random.Range(0, n); } while (next == target);
                target = next; break;
        }
    }

    void OnDrawGizmosSelected()
    {
        Gizmos.color = new Color(1f, .8f, .3f, 1f);
        for (int i = 0; i < waypoints.Count; i++)
        {
            if (waypoints[i] == null) continue;
            Gizmos.DrawSphere(waypoints[i].position + Vector3.up * 0.1f, 0.15f);
            if (i + 1 < waypoints.Count && waypoints[i + 1] != null) Gizmos.DrawLine(waypoints[i].position + Vector3.up * 0.1f, waypoints[i + 1].position + Vector3.up * 0.1f);
        }
        if (pattern == Pattern.Loop && waypoints.Count > 2 && waypoints[0] != null && waypoints[waypoints.Count - 1] != null)
            Gizmos.DrawLine(waypoints[waypoints.Count - 1].position + Vector3.up * 0.1f, waypoints[0].position + Vector3.up * 0.1f);
    }
}
