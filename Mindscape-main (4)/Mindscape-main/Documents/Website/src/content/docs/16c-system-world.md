---
id: system-world
group: Core Systems
nav: Shared City & Traffic
---

# Shared City & Traffic

Every story scene and the Tutorial share **one city model**, `Assets/Models/World/world_new.glb`. The streets, sidewalks, blocks of buildings, trees, street lights, benches and bus stops are the same everywhere; only the place you start (a house lot, the school campus, or the park) changes from scene to scene. The same city is **open world**: nothing but the city's outer edge stops you walking anywhere in it, and it is populated with sidewalk walkers and driving vehicles.

All of this is done by editor tools, so a new version of the model, or a new scene, takes a menu click rather than hand-placing hundreds of pieces.

## How a scene gets the city

The model is wrapped once as `Assets/Prefabs/World.prefab` (the model plus a `MeshCollider` on every solid part). Each scene then holds one instance of it, named `World`. `WorldModelSync` (`Assets/Editor/World/WorldModelSync.cs`) places that instance so it fits what the scene is already built on.

The model contains its own copy of the house lot (`World | House anchor`) and the school campus (`World | School anchor`), both at 1× scale. A scene keeps its **own** copy of the house or campus, because its doors, bed, story spots, routes and characters hang on those objects. The tool scales and turns the city so the matching anchor lands exactly on the scene's copy, then switches the city's duplicate off. No story coordinate ever moves.

| Scene type | Scenes | City scale | Fitted to |
| --- | --- | --- | --- |
| House | Ch 1 Ep 1, Ch 2 Ep 1 / 2 / 4 / 5, Ch 3 Ep 1 / 7 / 8 | 2.5× (the house is built at 2.5×) | `House And Lot`, turned 180° so the lot faces the road |
| School or reunion hall | Ch 1 Ep 2 to 4, Ch 2 Ep 3, Ch 3 Ep 2 to 6 | 2× (the campus is built at 2×) | the `School_Grounds` instance |
| Tutorial | `Tutorial` | 2× | the city park, east of the fountain; the old flat ground is switched off |

Because every step is repeatable, running the tool again on an already-fitted scene gives the same result.

### What the tool changes in a scene

- **Switches off the old street.** The house model's `Street |` parts (road, sidewalks, lights, houses across the road) are hidden, because the city's streets replace them. The city's own bus stop beside the lot or gate is hidden too; the scene's `Bus stop | shelter` stays, since the "Wait here" spot, the BUS sign and the moving bus hang on it.
- **Adds kerb ramps.** The city's pavement sits about 0.38 lower than the lot or campus entrance, and the player's `CharacterController` steps up 0.3 at most. A bare-collider wedge ("World kerb ramps", no mesh) runs from each entrance slab down to the pavement.
- **Seats the story bus on the road.** The scene's `School bus` is dropped so its wheels rest on the city road.
- **Opens the world** (next section).
- **Places street NPCs and traffic** (the two sections after that).

## Open world

`WorldModelSync` also removes everything that used to keep the player on a short stretch of street:

| Change | Why |
| --- | --- |
| `Road boundary`, `West route end`, `East route end` walls are switched off | They kept Chapter 2's player on the near sidewalk. |
| Chapter 3 Episode 7's `Neighborhood edge` walls are deleted | They were sized to the old street model. |
| The lot's `Pedestrian gate |` is switched off (the gate stands open) | So you can walk out of the house lot. |
| Cameras whose far clip is between 100 and 800 are raised to 800 | The whole city can be seen from far away. |
| One `World boundary` object adds four tall invisible walls just outside the city's outer slab | The only edge of the world; it stops the player falling into the void. |

> [!WARN] Story timers still run
>
> Episodes keep their free-play countdown, objectives and story spots. Open world only removes the walls, so a player can now wander away mid-episode. If you add an objective, give it a spot the player is guided to.

## Walkers stay on the pavement

In the house scenes, the near sidewalk is the paved strip `Block 31 | sidewalk end 21` (about z 22.6 to 27.6 in scene coordinates), then the road (27.6 to 47.6), then the far sidewalk (47.6 to 52.6). The old street had its sidewalk at z 21 to 24, which is grass in the city.

- **Street Life NPCs** (Maya, Leo, Nia, Hana, Malik, Officer Arthur) and the waypoints of their `... sidewalk route` objects are moved onto the strip by `WorldModelSync` (anything still on the lot side of the strip's inner 1.2 units), then set down on the ground. Re-running it moves nothing twice.
- **Ambient walkers and joggers** (`AmbientLifeBuilder.Routes`, house case) use pavement only: two walkers and a jogger on the far sidewalk, a jogger and a walker on the near sidewalk. The near routes stay east of the lot's entrance ramps. No route crosses the road.

## Traffic

`Assets/Models/Vehicles/` holds six vehicles: **Sedan, SUV, Pickup, SportsCar, DeliveryVan, SchoolBus**. Each `.glb` has five looping clips of about two seconds: one wheel roll per wheel and a body vibration. The models face **local −X** after import.

`CityTrafficBuilder` (`Assets/Editor/`) turns each model into `Assets/Prefabs/Vehicles/<Name>.prefab`: the model plus a `CityTrafficVehicle` component (`Assets/Vehicles/`) that holds the clips. `WorldModelSync` then adds a `City Traffic` object to every scene with **18 vehicles** (a mix of the six, buses kept rare).

### How the vehicles drive

The city's roads form a grid: east-west roads at z = ±26 and ±78 and north-south roads at x = ±51 and ±153 (model space), each 8 wide. Every one of the nine blocks gets a loop:

- It runs **clockwise** round the block in the right-hand lane, 1.7 units in from each road's centre, and rounds each corner with a short curve.
- Two vehicles share each loop, half a loop apart.
- Neighbouring blocks share a road but drive opposite ways on it, so each road carries two-way traffic.
- A loop turns at every corner, so it stays inside its own quarter of each intersection. Loops never cross, and vehicles never have to give way.

`CityTrafficVehicle` follows its loop forever (`path`, `speed`, `distance`). Each frame it samples the model's clips: the body clip in real time, the wheel clips at `speed / scale / modelRollSpeed` so the tyres turn exactly as fast as the road passes (the clips roll 2 turns per loop, which is 2.2 to 4.3 model units per second depending on the vehicle). Speeds are set in model units per second and multiplied by the city's scale, so a city at 2.5× drives 2.5× as fast.

> [!TIP] Vehicles have no colliders
>
> The player and NPCs walk through traffic, and the story's own parked school bus is not part of the traffic loops. This avoids a moving collider shoving the `CharacterController` around. Add a collider to the vehicle prefab if you want solid cars.

## Updating the model or the scene

| Menu item | What it does |
| --- | --- |
| `Mindscape ▸ World ▸ Rebuild World Prefab` | Re-wraps `world_new.glb` as `World.prefab` (use it after re-exporting the model). |
| `Mindscape ▸ World ▸ Rebuild Vehicle Prefabs` | Rebuilds the six vehicle prefabs. |
| `Mindscape ▸ World ▸ Apply World to Open Scene` | Fits the city, opens the world, and adds the street NPCs and traffic in the open scene. |
| `Mindscape ▸ World ▸ Apply World to All Story Scenes` | Does the same for every `Chapter N - Episode N` scene and the Tutorial. It opens, saves and closes each one, so save your own work first. |

1. Re-export `world_new.glb` into `Assets/Models/World/`. Keep the node names `World | House anchor`, `World | School anchor`, `World foundation`, `House | pedestrian approach`, `House | driveway approach` and `School | main gate approach`; the tool finds them by name.
2. Run **Rebuild World Prefab**. New parts get colliders (lane dashes, crosswalks, lights, trees and the park are left without them).
3. Run **Apply World to All Story Scenes** and check a house scene and a school scene.

The episode builders call `WorldModelSync.Apply` right before `AmbientLifeBuilder.Apply` every time they save a scene, so rebuilding an episode keeps its city.

> [!WARN] Performance
>
> The city is a few thousand renderers and colliders in every scene, plus 18 animated vehicles, and the camera now sees across all of it. Check frame rate on a WebGL and an Android build after changing the model.

> [!TIP] Known gap
>
> In the house scenes the story's bus shelter, route markers and "Wait here" spots were laid out for the old street, so they sit on the grass just behind the new sidewalk strip.
