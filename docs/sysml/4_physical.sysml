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
    port def ThrustCmdPort {
        out attribute thrust : Real;
    }
    // Position fix (sensor_msgs/NavSatFix).
    port def FixPort {
        out attribute latitude : Real;
        out attribute longitude : Real;
    }
    // Attitude and angular rate (sensor_msgs/Imu).
    port def ImuPort {
        out attribute yawRate : AngularVelocityValue;
    }
    // Telemetry to shore; in simulation, foxglove_bridge on a WebSocket.
    port def TelemetryPort {
        out attribute pose : Real[3];
    }

    // ---------- Hardware ----------
    part def Hull {
        attribute length : LengthValue;
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

    // ---------- ROS 2 software ----------
    part def Ros2Node {
        attribute packageName : String;
        attribute executable : String;
    }
    part def Nav2Stack {
        part plannerServer : Ros2Node;
        part controllerServer : Ros2Node;
    }

    part def Computer {
        port leftThrust : ThrustCmdPort;
        port rightThrust : ThrustCmdPort;
        port fix : ~FixPort;
        port imu : ~ImuPort;
        port telemetry : TelemetryPort;

        part nav2 : Nav2Stack;            // from milestone 2
        part rosGzBridge : Ros2Node;      // Gazebo <-> ROS 2 topics
        part foxgloveBridge : Ros2Node;   // telemetry to Lichtblick
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
    // Still to decide: localisation (milestone 2), chart model (milestones 2-4),
    // traffic picture and collision avoidance (milestone 5), mission manager.
    allocate LogicalArchitecture::logicalUsv.planner to physicalUsv.computer.nav2.plannerServer;
    allocate LogicalArchitecture::logicalUsv.controller to physicalUsv.computer.nav2.controllerServer;
}
