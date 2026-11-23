// Level 3 of 4 (Arcadia): logical architecture.
// How the USV works, in technology-independent components. Each system
// function from level 2 is allocated to the component that performs it.
package LogicalArchitecture {
    private import SystemAnalysis::*;

    // ---------- Data exchanged between components ----------
    item def Pose;           // position, heading and velocity
    item def NavigableArea;  // where the boat may go now: depth + tide + buoyage
    item def Tracks;         // other vessels and their predicted paths
    item def Route;          // planned path to the destination
    item def MotionCommand;  // desired speed and turn rate
    item def ModeCommand;    // manual, autonomous, stop

    port def PosePort { out item pose : Pose; }
    port def AreaPort { out item area : NavigableArea; }
    port def TracksPort { out item tracks : Tracks; }
    port def RoutePort { out item route : Route; }
    port def MotionPort { out item command : MotionCommand; }
    port def ModePort { out item mode : ModeCommand; }

    // ---------- Logical components ----------
    part def Localisation {
        doc /* Estimates the boat's pose from satellite positioning and inertial data. */
        port pose : PosePort;
    }
    part def ChartModel {
        doc /* Combines bathymetry, predicted tide and seamarks into the area that
             * is navigable right now. */
        port area : AreaPort;
    }
    part def TrafficPicture {
        doc /* Tracks other vessels from AIS and predicts their paths. */
        port tracks : TracksPort;
    }
    part def RoutePlanner {
        doc /* Plans a route through the navigable area to the destination. */
        port pose : ~PosePort;
        port area : ~AreaPort;
        port route : RoutePort;
    }
    part def CollisionAvoidance {
        doc /* Adjusts the route around other vessels following the COLREGs. */
        port pose : ~PosePort;
        port tracks : ~TracksPort;
        port routeIn : ~RoutePort;
        port routeOut : RoutePort;
    }
    part def MotionController {
        doc /* Follows the route and turns it into motion commands. */
        port pose : ~PosePort;
        port route : ~RoutePort;
        port mode : ~ModePort;
        port command : MotionPort;
    }
    part def MissionManager {
        doc /* Receives missions and commands from shore and decides the operating
             * mode. */
        port mode : ModePort;
    }

    part def LogicalUSV {
        part localisation : Localisation;
        part chart : ChartModel;
        part traffic : TrafficPicture;
        part planner : RoutePlanner;
        part avoidance : CollisionAvoidance;
        part controller : MotionController;
        part mission : MissionManager;

        connect localisation.pose to planner.pose;
        connect localisation.pose to avoidance.pose;
        connect localisation.pose to controller.pose;
        connect chart.area to planner.area;
        connect traffic.tracks to avoidance.tracks;
        connect planner.route to avoidance.routeIn;
        connect avoidance.routeOut to controller.route;
        connect mission.mode to controller.mode;
    }

    part logicalUsv : LogicalUSV;

    // ---------- Allocation of system functions (level 2 -> level 3) ----------
    allocate SystemAnalysis::usvFunctions.planRoute to logicalUsv.planner;
    allocate SystemAnalysis::usvFunctions.avoidShallowWater to logicalUsv.chart;
    allocate SystemAnalysis::usvFunctions.keepToChannel to logicalUsv.chart;
    allocate SystemAnalysis::usvFunctions.buildTrafficPicture to logicalUsv.traffic;
    allocate SystemAnalysis::usvFunctions.avoidCollision to logicalUsv.avoidance;
    allocate SystemAnalysis::usvFunctions.followRoute to logicalUsv.controller;
    allocate SystemAnalysis::usvFunctions.reportTelemetry to logicalUsv.mission;
    allocate SystemAnalysis::usvFunctions.stopOnCommand to logicalUsv.mission;

    // ---------- Behaviour of the mission manager ----------
    // Milestone 1 uses Idle, Manual and Stopped; autonomous modes arrive
    // with Nav2 in milestone 2 and collision avoidance in milestone 5.
    state def OperatingMode {
        entry; then Idle;

        state Idle;
        state Manual;
        state Autonomous {
            entry; then FollowingRoute;
            state FollowingRoute;
            state AvoidingCollision;
            transition give_way first FollowingRoute then AvoidingCollision;
            transition clear first AvoidingCollision then FollowingRoute;
        }
        state Stopped;   // thrust forced to zero

        transition take_control first Idle then Manual;
        transition start_mission first Idle then Autonomous;
        transition stop_manual first Manual then Stopped;
        transition stop_autonomous first Autonomous then Stopped;
        transition reset first Stopped then Idle;
    }
}
