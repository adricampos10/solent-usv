# solent-usv

I'm building a simulated **autonomous surface vessel (USV)** that plans and follows routes across the **Solent** (Portsmouth, Southampton and the Isle of Wight) with **ROS 2 Jazzy + Nav2**. It runs in the **VRX** (Virtual RobotX) simulator on **Gazebo Harmonic**, and every route plan uses real open data: depth, tide height and buoyage.

> Work in progress.

> [!WARNING]
> **Not for navigation.** This is a simulation and portfolio project. The bathymetry, seamarks and tide data it uses are coarse, incomplete and possibly out of date, and I process them in simplified ways. Never use anything in this repository to plan or navigate a real vessel. Use official charts (UKHO/ADMIRALTY), Notices to Mariners and proper passage planning.

## What I'm building
- A WAM-V from VRX in a georeferenced Solent world, driven by Nav2.
- A costmap built from real bathymetry: anywhere shallower than the boat's draft plus a safety margin is a no-go area.
- Tide-aware planning: charted depth plus predicted tide height, so a route that is open at high water is blocked at low water.
- Routes that respect IALA region A buoyage (port and starboard lateral marks, cardinal marks) taken from OpenSeaMap.
- Collision avoidance with other vessels following the COLREGs (head-on, crossing, overtaking).
- A scenario suite with metrics and GitHub Actions CI, as in my [warehouse-nav2](https://github.com/adricampos10/warehouse-nav2) project.

## Roadmap
1. **VRX in Docker.** The VRX `jazzy` branch (ROS 2 Jazzy + Gazebo Harmonic) runs headless in Docker on my Mac, with a WAM-V that I can drive and watch in Lichtblick through `foxglove_bridge`.
2. **Bathymetry costmap.** I download an EMODnet DTM tile for the Solent and turn it into a Nav2 map where depth < draft + margin is lethal. Pure Python, unit-tested with pytest.
3. **Tides.** I add the predicted tide height to the charted depth (both referenced to chart datum, roughly LAT), so the costmap changes with time. A scenario checks that the same route passes at high water and fails at low water.
4. **IALA A buoyage.** Lateral and cardinal marks from OpenSeaMap become costmap constraints, so the boat keeps the correct side of each channel.
5. **COLREGs.** Other vessels (simulated targets) and a collision avoidance layer that applies Rules 13–15 and checks CPA/TCPA.
6. **Scenarios and CI.** YAML scenarios (start, goals, tide time, traffic, expected result), metrics with no ROS imports, and a GitHub Actions matrix with one job per scenario.

## Data sources
| Data | Source | Licence | How I use it |
|---|---|---|---|
| Bathymetry | [EMODnet Bathymetry](https://emodnet.ec.europa.eu/en/bathymetry) DTM, about 115 m grid, depths referenced to LAT | CC BY 4.0 | Download once with a WCS request and store a small tile |
| Seamarks | [OpenSeaMap](https://www.openseamap.org/) `seamark:*` tags from OpenStreetMap, through the Overpass API | ODbL, © OpenStreetMap contributors | Query once and store a GeoJSON snapshot |
| Tides | [ADMIRALTY UK Tidal API](https://admiraltyapi.portal.azure-api.net/), Discovery tier (free) | UKHO terms | High and low water times and heights; needs a free API key |

I don't use Navionics or any other proprietary chart data.
