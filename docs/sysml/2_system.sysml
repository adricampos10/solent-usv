// Level 2 of 4 (Arcadia): system analysis.
// The autonomous boat appears as a black box: what it must do and what it
// exchanges with its environment, not how it is built. The system
// requirements live here.
package SystemAnalysis {
    private import ISQ::*;
    private import SI::*;
    private import ScalarValues::*;
    private import OperationalAnalysis::*;

    // ---------- External interfaces ----------
    item def Mission {
        doc /* Destination and departure time from the operator. */
    }
    item def Telemetry {
        doc /* Position, heading, speed and current mode. */
    }
    item def AisReport {
        doc /* Position, course and identity of another vessel. */
    }

    port def OperatorLinkPort {
        in item mission : Mission;
        out item telemetry : Telemetry;
    }
    port def AisPort {
        in item report : AisReport;
    }

    // ---------- The system as a black box ----------
    part def USV {
        attribute draft : LengthValue;
        port operatorLink : OperatorLinkPort;
        port ais : AisPort;
    }

    // System context: the boat placed in the operational world of level 1.
    part def SolentContext {
        part usv : USV;
        part operator : MissionOperator {
            port link : ~OperatorLinkPort;
        }
        part traffic : Vessel[0..*] {
            port ais : ~AisPort;
        }
        connect operator.link to usv.operatorLink;
        connect traffic.ais to usv.ais;
    }

    // ---------- System functions ----------
    action def PlanRoute;
    action def FollowRoute;
    action def AvoidShallowWater;
    action def KeepToChannel;
    action def BuildTrafficPicture;
    action def AvoidCollision;
    action def ReportTelemetry;
    action def StopOnCommand;

    action usvFunctions {
        action planRoute : PlanRoute;
        action followRoute : FollowRoute;
        action avoidShallowWater : AvoidShallowWater;
        action keepToChannel : KeepToChannel;
        action buildTrafficPicture : BuildTrafficPicture;
        action avoidCollision : AvoidCollision;
        action reportTelemetry : ReportTelemetry;
        action stopOnCommand : StopOnCommand;
    }

    // ---------- System capability ----------
    use case def AutonomousTransit {
        doc /* The USV takes a mission from the operator and transits the Solent
             * on its own: level-1 capability TransitTheSolent, now with the
             * boat in it. */
        subject usv : USV;
        actor operator : MissionOperator;
        actor traffic : Vessel[0..*];
        objective {
            doc /* Reach the destination meeting R2.1-R2.6. */
        }
    }

    // ---------- System requirements (derived from the level-1 rules) ----------
    requirement def <'R2.1'> UnderKeelClearance {
        doc /* The USV shall not plan or follow a route through water where charted
             * depth plus predicted height of tide is less than its draft plus
             * the safety margin. */
        subject usv : USV;
        attribute safetyMargin : LengthValue;
    }
    requirement def <'R2.2'> ChannelSide {
        doc /* In a buoyed channel, the USV shall keep the IALA A lateral marks on
             * the correct side for its direction of travel. */
        subject usv : USV;
    }
    requirement def <'R2.3'> GiveWayWhenCrossing {
        doc /* When crossing with another vessel on its starboard side, the USV shall
             * give way, keeping the closest point of approach above a minimum. */
        subject usv : USV;
        attribute minCpa : LengthValue;
    }
    requirement def <'R2.4'> KeepOutOfMpz {
        doc /* The USV shall never enter the Moving Prohibited Zone of a large ship. */
        subject usv : USV;
    }
    requirement def <'R2.5'> TelemetryRate {
        doc /* The USV shall report its position to the operator at least once a second. */
        subject usv : USV;
        attribute minRate : FrequencyValue = 1 [Hz];
    }
    requirement def <'R2.6'> StopCommand {
        doc /* On a stop command, the USV shall set thrust to zero within 1 s. */
        subject usv : USV;
        attribute maxDelay : TimeValue = 1 [s];
    }

    requirement systemRequirements {
        subject usv : USV;
        requirement underKeel : UnderKeelClearance;
        requirement channelSide : ChannelSide;
        requirement giveWay : GiveWayWhenCrossing;
        requirement mpz : KeepOutOfMpz;
        requirement telemetry : TelemetryRate;
        requirement stop : StopCommand;
    }

    // Traceability to level 1: each system requirement derives from a rule.
    dependency UnderKeelClearance to KeepUnderKeelClearance;
    dependency ChannelSide to FollowIalaA;
    dependency GiveWayWhenCrossing to ColregsSteeringRules;
    dependency KeepOutOfMpz to MovingProhibitedZone;
}
