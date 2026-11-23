// Verification: the simulation that stands in for the real boat, the
// requirements on it for milestone 1, and the tests that verify them.
package Verification {
    private import ISQ::*;
    private import SI::*;
    private import ScalarValues::*;
    private import PhysicalArchitecture::*;

    // VRX in Docker: Gazebo plays the hull, thrusters and sensors.
    part def SimulationStack {
        attribute realTimeFactor : Real;   // simulated seconds per wall-clock second
        attribute headless : Boolean;
        part usv : PhysicalUSV;
        part tidalCurrent : TidalCurrentGenerator;   // from milestone 5
    }

    // VRX has no current: my own Python node pushes the hull through Gazebo's
    // wrench topic, with strength and direction following the tide.
    part def TidalCurrentGenerator {
        attribute maxSpeed : SpeedValue;
    }

    // ---------- Milestone 1: VRX in Docker ----------
    requirement def <'R1.1'> HeadlessSimulation {
        doc /* The simulation shall run headless in Docker on an arm64 Mac without an NVIDIA GPU. */
        subject sim : SimulationStack;
        require constraint { sim.headless }
    }
    requirement def <'R1.2'> RealTimePerformance {
        doc /* The simulation shall run at a real-time factor of at least 0.5. */
        subject sim : SimulationStack;
        attribute minRealTimeFactor : Real = 0.5;
        require constraint { sim.realTimeFactor >= minRealTimeFactor }
    }
    requirement def <'R1.3'> ForwardThrust {
        doc /* With equal positive thrust on both thrusters, the USV shall move forward
             * at least 5 m within 20 s. */
        subject sim : SimulationStack;
        attribute minDistance : LengthValue = 5 [m];
        attribute timeLimit : TimeValue = 20 [s];
    }
    requirement def <'R1.4'> DifferentialTurn {
        doc /* With opposite thrust on the two thrusters, the USV shall turn on the spot,
             * with yaw rate in the direction of the stronger forward thruster. */
        subject sim : SimulationStack;
    }
    requirement def <'R1.5'> Visualisation {
        doc /* The pose of the USV shall be visible in Lichtblick through foxglove_bridge. */
        subject sim : SimulationStack;
    }

    requirement milestone1Requirements {
        subject sim : SimulationStack;
        requirement headless : HeadlessSimulation;
        requirement performance : RealTimePerformance;
        requirement forward : ForwardThrust;
        requirement turn : DifferentialTurn;
        requirement visualisation : Visualisation;
    }

    part milestone1 : SimulationStack;
    satisfy milestone1Requirements by milestone1;

    // Smoke test (scripts/run_smoke_test.sh): starts the headless simulation,
    // applies thrust and checks the motion from odometry. R1.5 is checked by eye.
    verification def SmokeTest {
        subject sim : SimulationStack;
        objective {
            verify milestone1Requirements.headless;
            verify milestone1Requirements.performance;
            verify milestone1Requirements.forward;
            verify milestone1Requirements.turn;
        }
    }
}
