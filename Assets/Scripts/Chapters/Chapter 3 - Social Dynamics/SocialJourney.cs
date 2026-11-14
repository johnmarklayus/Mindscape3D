using System.Collections;
using System.Linq;
using Mindscape.AcademicPressure;
using UnityEngine;
using static Mindscape.AcademicPressure.StoryWords;

namespace Mindscape.SocialDynamics
{
    // Episode 1 ends by getting ready and going: change in the bathroom, out of the front door, down to the bus stop,
    // and the bus to the reunion. Episode 2 starts as the bus pulls in outside the hall. In Episode 5 Joey steps out to
    // a little park for some air, and Justin comes to find him there.
    public sealed partial class SocialDynamicsEpisode
    {
        // ================================================================ Episode 1 · getting ready, the bus

        IEnumerator GetReadyAndGo()
        {
            bool dressed = false, outside = false, atStop = false;
            var bath = AddBathroom("Get changed for the reunion", () => !dressed, Outfit.GoingOut,
                "This shirt still fits. Okay. I can do this.", () => dressed = true);
            if (bath != null)
            {
                yield return Think(W("I should get changed before I go."));
                SetObjective(W("Getting ready"), Check(false, W("Change in the bathroom")));
                yield return RoamUntil(() => dressed);
            }
            else PlayerOutfit.Wear(player, Outfit.GoingOut);

            // Out of the front door (it opens with its own [ E ]).
            HomeWelcome.FrontDoor(spawn.position, out var door, out var inward);
            Vector3 step = Ground(door - inward * 2.6f, door.y) + Vector3.up * .1f;
            AddArrival(Waypoint("Outside the front door", step), W("Head out"), () => !outside, () => { outside = true; return Think(W("The reunion is across town. The bus will get me there.")); }, 2f);
            SetObjective(W("Head out"), Check(true, W("Changed")) + Check(false, W("Out the front door")));
            yield return RoamUntil(() => outside);

            var ride = BusRide.Find();
            if (ride == null) { yield return Card(W("On the way to the reunion"), W("Continue  [Space]")); yield break; }
            Vector3 kerb = Ground(ride.kerb, step.y);
            AddArrival(Waypoint("At the bus stop", kerb + Vector3.up * .1f), W("Walk to the bus stop"), () => !atStop, () => { atStop = true; return Nothing(); }, 3f);
            SetObjective(W("To the bus stop"), Check(true, W("Out the front door")) + Check(false, W("The bus stop down the street")));
            yield return RoamUntil(() => atStop);

            // The bus pulls in at the shelter.
            SetLocked(true);
            Vector3 toKerb = Flat(kerb - ride.stop).normalized;
            Teleport(kerb + Vector3.up * .1f, Quaternion.LookRotation(-toKerb).eulerAngles.y);
            ride.Place(-70);
            Shot(kerb + toKerb * 6 - ride.heading * 7 + Vector3.up * 4, ride.stop + Vector3.up * 2);
            ShotFocus.Clear();
            yield return ride.Drive(-70, 0, 6f, true);
            yield return Think(W("Here it is. No turning back now."));
            // On board; the camera follows the bus down the road.
            yield return Fade(0, 1, .4f);
            player.gameObject.SetActive(false);
            yield return Fade(1, 0, .4f);
            bool gone = false;
            StartCoroutine(ride.Drive(0, 140, 9f, false, () =>
                Shot(ride.bus.position + toKerb * 19 + Vector3.up * 8.5f - ride.heading * 14, ride.bus.position + Vector3.up * 2f)));
            StartCoroutine(After(9f, () => gone = true));
            yield return Think(W("Everyone will be there. I hope I still remember how to talk to them."));
            while (!gone) yield return null;
            yield return Card(W("On the way to the reunion"), W("Continue  [Space]"));
            player.gameObject.SetActive(true);
        }

        static IEnumerator After(float seconds, System.Action then) { yield return new WaitForSeconds(seconds); then(); }
        static IEnumerator Then(IEnumerator first, System.Action then) { yield return first; then(); }

        // ================================================================ Episode 2 · arriving by bus

        // The hall's front doors (the middle of its south wall, seen from inside), and the way in.
        bool HallDoors(out Vector3 inside, out Vector3 outside, out Vector3 inward)
        {
            float floorY = spawn.position.y;
            Vector3 centre = new Vector3(0, floorY + 1.5f, 0);
            inward = Vector3.forward; inside = spawn.position; outside = spawn.position - Vector3.forward * 4;
            foreach (var hit in Physics.RaycastAll(centre, Vector3.back, 30, ~0, QueryTriggerInteraction.Ignore).OrderBy(h => h.distance))
            {
                if (hit.collider.GetComponentInParent<CharacterController>() != null || hit.collider.GetComponentInParent<NPC>() != null) continue;
                inside = new Vector3(0, floorY, hit.point.z + 1.6f);
                outside = Ground(new Vector3(0, floorY, hit.point.z - 2.6f), floorY);
                return true;
            }
            return false;
        }

        // Episode 2 starts where Episode 1 left off, on the bus: it pulls in on the road outside the hall, Joey steps
        // off and walks up to the doors, and then the party inside.
        IEnumerator ArriveByBus()
        {
            if (!HallDoors(out var inside, out var outside, out var inward)) yield break;
            var ride = BusRide.FindNear(outside);
            if (ride == null) yield break;
            SetLocked(true);
            player.gameObject.SetActive(false);
            Vector3 kerb = Ground(ride.kerb + ride.heading * 2.5f, outside.y);
            Vector3 toKerb = Flat(kerb - ride.stop).normalized;
            ride.Place(-70);
            Shot(kerb + toKerb * 7 - ride.heading * 9 + Vector3.up * 4.2f, ride.stop + Vector3.up * 2);
            ShotFocus.Clear();
            yield return ride.Drive(-70, 0, 6f, true);
            player.gameObject.SetActive(true);
            Teleport(kerb + Vector3.up * .1f, Quaternion.LookRotation(Flat(outside - kerb)).eulerAngles.y);
            // Away down the road, then out of the traffic (a parked bus would hold the lane up for good).
            StartCoroutine(Then(ride.Drive(0, 140, 9f, false), () => ride.bus.gameObject.SetActive(false)));
            // From beside the doors, back toward the road: Joey on the pavement, the bus pulling away behind him.
            Vector3 side = Vector3.Cross(Vector3.up, inward);
            Vector3 eye = HomeWelcome.ClearView(outside + Vector3.up * 2.2f, outside - inward * 1.5f + side * 4.5f + Vector3.up * 3.4f);
            Shot(eye, (kerb + outside) * .5f + Vector3.up * 1.8f);
            ShotFocus.Clear();
            yield return Think(W("This is the place. I can hear music from inside."));
            yield return WalkTo(outside, Quaternion.LookRotation(inward).eulerAngles.y, Mathf.Clamp(Vector3.Distance(Flat(kerb), Flat(outside)) / 2.4f, 1.5f, 5f));
            yield return Think(W("Okay. Just say hello. That's all I have to do."));
            yield return Fade(0, 1, .5f);
            Teleport(ClearSpawn(), spawn.eulerAngles.y);
            Shot(openingView.position, openingView.position + openingView.forward * 8);
            yield return Fade(1, 0, .6f);
        }

        // ================================================================ Episode 5 · the little park

        static readonly string[] ParkLines = { "Justin|Hey. I was wondering where you went.", "Me|Sorry. I just needed some time alone.", "Justin|You don't have to apologize. I just wanted to check if you're okay.", "Me|Honestly, I'm not sure.", "Me|Everyone has so much to talk about. Their jobs, their plans, the things they've achieved.", "Me|I'm happy for them. I really am. But when I hear all those stories, I start thinking about my own life.", "Justin|What do you think about?", "Me|I think about the things I should have done by now. The things I could have continued. The opportunities I might have missed.", "Me|And then I start wondering if everyone else is going to notice that I'm not where I thought I'd be.", "Justin|Can I tell you something?", "Me|Sure.", "Justin|I used to feel that way, too.", "Justin|There was a time when I thought everyone around me was doing better. I'd go home wondering why I wasn't doing the same things.", "Me|You did?", "Justin|Yeah. I just didn't talk about it much.", "Justin|Sometimes I thought I had to prove I was doing well. I was afraid people would think I was wasting my time.", "Justin|I realized I was spending so much time trying to look successful that I wasn't enjoying the life I had.", "Me|So what did you do?", "Justin|I started paying attention to what mattered to me, instead of asking whether I was doing better than someone else.", "Justin|I'm still figuring things out. I don't have everything planned, either.", "Me|But you seem like you know what you're doing.", "Justin|That's what it might look like from the outside. But I still have days when I feel lost.", "Justin|You don't need to prove yourself to others. You just need to be yourself and accept who you are.", "Me|I don't know if I can do that so easily.", "Justin|You don't have to figure it out tonight.", "Justin|You don't have to become someone impressive just to deserve being here. We invited you because you're our friend. Not because we expected a list of achievements.", "Me|I guess I forgot that.", "Justin|Then let me remind you. You still matter, even when you don't feel proud of yourself.", "Me|Thank you for coming to check on me.", "Justin|Of course. That's what friends are for.", "Justin|Come on. You don't have to tell everyone your whole life story. Just come sit with us for a while." };

        // Joey slips out of the hall first, to the little park outside with its fountain and lights. A moment alone, then
        // footsteps: Justin noticed he had gone and comes looking for him. They talk by the fountain, then go back in.
        IEnumerator ParkTalk()
        {
            var justin = transform.Find("Justin");
            Vector3 justinWas = justin != null ? justin.position : Vector3.zero; Quaternion justinTurn = justin != null ? justin.rotation : Quaternion.identity;
            HallDoors(out var doorsInside, out _, out var inward);

            yield return Fade(0, 1, .7f);
            var park = SocialStaging.Park(ParkOrigin());
            Vector3 toFountain = Flat(park.fountain - park.joey).normalized, across = Vector3.Cross(Vector3.up, toFountain);
            Teleport(park.joey + Vector3.up * .1f, Quaternion.LookRotation(toFountain).eulerAngles.y);
            // The rig's origin sits a little above its feet: keep that height above the lawn.
            float lift = justin != null ? justinWas.y - Ground(justinWas, justinWas.y).y : 0;
            Vector3 justinFrom = park.justinFrom + Vector3.up * lift, justinTo = park.justinTo + Vector3.up * lift;
            if (justin != null) HomeWelcome.Place(justin, justinFrom, park.joey);
            float h = PlayerHeight();
            Vector3 look = park.fountain + Vector3.up * h * .6f;
            // From behind and beside Joey: the fountain and the lights ahead.
            Shot(park.joey - toFountain * 6.5f + across * 3f + Vector3.up * h * 1.1f, look);
            ShotFocus.Clear();
            yield return Fade(1, 0, 1f);
            var drift = StartCoroutine(Glide(park.joey - toFountain * 4.5f - across * 2.6f + Vector3.up * h * .8f, look, 7f));
            yield return Think(W("It's quieter out here. Just the water and the lights."));
            yield return Think(W("Maybe nobody will notice I'm gone."));
            StopCoroutine(drift);

            // Footsteps on the path: Justin, looking for him.
            if (justin != null)
            {
                Shot(park.joey + toFountain * 3.2f + across * 2.4f + Vector3.up * h * .75f, (park.joey + park.justinTo) * .5f + Vector3.up * h * .5f);
                ShotFocus.Clear();
                var walk = StartCoroutine(HomeWelcome.StepToward(justin, justinTo, 4.2f));
                yield return Think(W("Footsteps on the path behind me."));
                yield return walk;
                StartCoroutine(Turn(player, Quaternion.LookRotation(Flat(justin.position - player.position)), .5f));
                yield return HomeWelcome.TurnTo(justin, player.position, .4f);
            }
            yield return Lines(ParkLines);

            // Back inside together, just in from the doors.
            yield return Fade(0, 1, .7f);
            Destroy(park.gameObject);
            Teleport(doorsInside, Quaternion.LookRotation(inward).eulerAngles.y);
            if (justin != null)
            {
                Vector3 side = Vector3.Cross(Vector3.up, inward);
                HomeWelcome.Place(justin, HomeWelcome.ClearFloor(doorsInside + side * 1.6f + inward * .4f, justinWas.y), doorsInside + inward * 6);
                HomeWelcome.Play(justin, "Idle");
            }
            Shot(openingView.position, doorsInside + inward * 3 + Vector3.up * 2);
            yield return Fade(1, 0, .7f);
        }

        // Far beyond everything in the scene, so no part of the city or the school shows in the park.
        Vector3 ParkOrigin()
        {
            var renderers = FindObjectsByType<Renderer>(FindObjectsSortMode.None);
            if (renderers.Length == 0) return new Vector3(2000, 0, 0);
            var b = renderers[0].bounds; foreach (var r in renderers) b.Encapsulate(r.bounds);
            return new Vector3(b.max.x + 150, 0, b.center.z);
        }
    }
}
