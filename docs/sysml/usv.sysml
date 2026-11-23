// solent-usv system model, milestone 1: VRX in Docker.
// I write the model before the code. Every requirement says which part
// satisfies it and which test verifies it.
package SolentUSV {
    private import ISQ::*;
    private import SI::*;
    private import ScalarValues::*;

    // ---------- Interfaces ----------
    // Thrust command from the computer to one thruster, normalised to [-1, 1].
    // In VRX it is the ROS 2 topic /wamv/thrusters/<side>/thrust (std_msgs/Float64).
    port def ThrustCmdPort {
        out attribute thrust : Real;
    }

    // Position fix from the GNSS receiver (sensor_msgs/NavSatFix in ROS 2).
    port def FixPort {
        out attribute latitude : Real;
        out attribute longitude : Real;
    }

    // Attitude and angular rate from the IMU (sensor_msgs/Imu in ROS 2).
    port def ImuPort {
        out attribute yawRate : AngularVelocityValue;
    }

    // Telemetry to the shore station; in simulation it is foxglove_bridge on a WebSocket.
    port def TelemetryPort {
        out attribute pose : Real[3];
    }

    // ---------- Structure (block definition diagram) ----------
    part def Hull {
        attribute length : LengthValue;
        attribute beam : LengthValue;
        attribute draft : LengthValue;
        attribute mass : MassValue;
    }

    part def Thruster {
        port cmd : ~ThrustCmdPort;
    }

    part def GnssReceiver {
        port fix : FixPort;
    }

    part def Imu {
        port imu : ImuPort;
    }

    part def RadioLink {
        port telemetry : ~TelemetryPort;
    }

    part def Computer {
        port leftThrust : ThrustCmdPort;
        port rightThrust : ThrustCmdPort;
        port fix : ~FixPort;
        port imu : ~ImuPort;
        port telemetry : TelemetryPort;
    }

    // WAM-V: twin-hull USV with one fixed thruster per hull (differential thrust).
    part def USV {
        part hull : Hull {
            attribute :>> length = 4.9 [m];
            attribute :>> mass = 180.0 [kg];   // base link mass in the VRX model
        }
        part leftThruster : Thruster;
        part rightThruster : Thruster;
        part gnss : GnssReceiver;
        part imu : Imu;
        part computer : Computer;
        part radio : RadioLink;

        // Internal connections (internal block diagram)
        connect computer.leftThrust to leftThruster.cmd;
        connect computer.rightThrust to rightThruster.cmd;
        connect gnss.fix to computer.fix;
        connect imu.imu to computer.imu;
        connect computer.telemetry to radio.telemetry;
    }

    // Simulation stack that replaces the real boat in milestone 1.
    part def SimulationStack {
        attribute realTimeFactor : Real;   // simulated seconds per wall-clock second
        attribute headless : Boolean;
        part usv : USV;
    }

    // ---------- Behaviour ----------
    // Milestone 1 only needs manual control. Autonomous and COLREG avoidance
    // modes come in later milestones.
    state def OperatingMode {
        entry; then Idle;

        state Idle;
        state Manual;
        state Stopped;   // thrust forced to zero

        transition idleToManual first Idle then Manual;
        transition manualToStopped first Manual then Stopped;
        transition stoppedToIdle first Stopped then Idle;
    }

    // ---------- Requirements ----------
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
        subject usv : USV;
        attribute minDistance : LengthValue = 5 [m];
        attribute timeLimit : TimeValue = 20 [s];
    }

    requirement def <'R1.4'> DifferentialTurn {
        doc /* With opposite thrust on the two thrusters, the USV shall turn on the spot,
             * with yaw rate in the direction of the stronger forward thruster. */
        subject usv : USV;
    }

    requirement def <'R1.5'> Visualisation {
        doc /* The pose of the USV shall be visible in Lichtblick through foxglove_bridge. */
        subject sim : SimulationStack;
    }

    // ---------- Milestone 1 context: who satisfies what, and how it is verified ----------
    part milestone1 : SimulationStack;

    requirement milestone1Requirements {
        subject sim : SimulationStack;
        requirement headless : HeadlessSimulation;
        requirement performance : RealTimePerformance;
        requirement forward : ForwardThrust;
        requirement turn : DifferentialTurn;
        requirement visualisation : Visualisation;
    }

    satisfy milestone1Requirements by milestone1;

    // Smoke test (scripts/run_smoke_test.sh): starts the headless simulation,
    // applies thrust and checks the motion from odometry.
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
