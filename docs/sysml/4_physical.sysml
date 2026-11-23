// Level 4 of 4 (Arcadia): physical architecture.
// What implements the logical components: hardware (in simulation, the VRX
// WAM-V in Gazebo) and ROS 2 software. Only decided components appear here;
// the rest are added milestone by milestone.
package PhysicalArchitecture {
    private import ISQ::*;
    private import SI::*;
    private import ScalarValues::*;
    private import LogicalArchitecture::*;

    // ---------- Physical interfaces ----------
    // Thrust command to one thruster, normalised to [-1, 1].
    // In VRX: ROS 2 topic /wamv/thrusters/<side>/thrust (std_msgs/Float64).
    port def Thrust {
        out attribute thrust : Real;
    }
    // Position fix (sensor_msgs/NavSatFix).
    port def Fix {
        out attribute latitude : Real;
        out attribute longitude : Real;
    }
    // Attitude and angular rate (sensor_msgs/Imu).
    port def Inertial {
        out attribute yawRate : AngularVelocityValue;
    }
    // Telemetry to shore; in simulation, foxglove_bridge on a WebSocket.
    port def Downlink {
        out attribute pose : Real[3];
    }

    // ---------- Hardware ----------
    part def Hull {
        attribute length : LengthValue;
        attribute mass : MassValue;
    }
    part def Thruster {
        port cmd : ~Thrust;
    }
    part def GnssReceiver {
        port fix : Fix;
    }
    part def Imu {
        port imu : Inertial;
    }
    part def RadioLink {
        port telemetry : ~Downlink;
    }

    // ---------- ROS 2 software ----------
    // No Nav2 and no third-party autopilot: I write the planner, guidance and
    // control nodes myself, in Python first (an optional later milestone ports
    // guidance and control to C++ and checks both give the same results).
    part def Ros2Node {
        attribute packageName : String;
        attribute executable : String;
        attribute implementation : String;
    }

    part def Computer {
        port leftThrust : Thrust;
        port rightThrust : Thrust;
        port fix : ~Fix;
        port imu : ~Inertial;
        port telemetry : Downlink;

        part motionController : Ros2Node {   // milestone 2: LOS/ILOS, PID, thrust mixer
            attribute :>> implementation = "Python";
        }
        part routePlanner : Ros2Node {       // milestone 3: A* on the chart grid
            attribute :>> implementation = "Python";
        }
        part rosGzBridge : Ros2Node;         // Gazebo <-> ROS 2 topics
        part foxgloveBridge : Ros2Node;      // telemetry to Lichtblick
    }

    // WAM-V: twin-hull USV with one fixed thruster per hull (differential thrust).
    part def PhysicalUSV {
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

        connect computer.leftThrust to leftThruster.cmd;
        connect computer.rightThrust to rightThruster.cmd;
        connect gnss.fix to computer.fix;
        connect imu.imu to computer.imu;
        connect computer.telemetry to radio.telemetry;
    }

    part physicalUsv : PhysicalUSV;

    // ---------- Allocation of logical components (level 3 -> level 4) ----------
    // Still to decide: localisation (milestone 2), chart model (milestones 3-5),
    // traffic picture and collision avoidance (milestone 6), mission manager.
    allocate LogicalArchitecture::logicalUsv.controller to physicalUsv.computer.motionController;
    allocate LogicalArchitecture::logicalUsv.planner to physicalUsv.computer.routePlanner;
}
