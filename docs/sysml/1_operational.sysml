// Level 1 of 4 (Arcadia): operational analysis.
// The Solent as it is today, its users and its rules. The autonomous boat
// does not appear at this level: I describe the problem before the solution.
package OperationalAnalysis {
    private import ScalarValues::*;

    // ---------- Operational entities and actors ----------
    part def Waterway {
        doc /* The Solent, Southampton Water and Portsmouth Harbour: charted depth,
             * tide, tidal streams, buoyed channels and the Precautionary Area. */
    }

    part def Vessel {
        attribute lengthOverall : ISQ::LengthValue;
        attribute broadcastsAis : Boolean;
    }
    part def Ferry :> Vessel {
        doc /* Scheduled passenger and vehicle ferries on fixed routes, e.g.
             * Portsmouth-Fishbourne, Southampton-Cowes, Gosport. */
    }
    part def LargeShip :> Vessel {
        doc /* Container ships, cruise ships and tankers of 150 m or more,
             * restricted to the deep-water channel. */
    }
    part def SmallCraft :> Vessel {
        doc /* Yachts, dinghies, RIBs and fishing boats; many carry no AIS. */
    }

    part def VesselTrafficService {
        doc /* Southampton VTS and the Queen's Harbour Master Portsmouth:
             * monitor traffic and give instructions on VHF. */
    }

    part def MissionOperator {
        doc /* The person or organisation that needs work done at sea,
             * e.g. moving between harbours or surveying an area. */
    }

    // ---------- Rules that apply to everyone on the water ----------
    // Not system requirements yet: they constrain any vessel, crewed or not.
    requirement def <'OR1'> KeepUnderKeelClearance {
        doc /* A vessel keeps enough water under its keel: charted depth plus
             * height of tide minus draft stays above a safety margin. */
    }
    requirement def <'OR2'> FollowIalaA {
        doc /* In IALA region A, entering harbour, red (port) lateral marks
             * are left to port and green (starboard) marks to starboard. */
    }
    requirement def <'OR3'> ColregsSteeringRules {
        doc /* COLREGs Rules 13-15: an overtaking vessel keeps clear; head-on,
             * both alter to starboard; crossing, the vessel that has the
             * other on her starboard side gives way. */
    }
    requirement def <'OR4'> NarrowChannels {
        doc /* COLREGs Rule 9: a vessel under 20 m or a sailing vessel does not
             * impede a vessel that can navigate only within the channel. */
    }
    requirement def <'OR5'> MovingProhibitedZone {
        doc /* Local rule of the Port of Southampton: in the Precautionary Area,
             * vessels under 20 m and all sailing vessels keep out of the zone
             * 1000 m ahead and 100 m either side of a large ship. */
    }

    // ---------- Operational activities ----------
    action def TransitBetweenHarbours;
    action def KeepToNavigableWater;
    action def KeepToBuoyedChannel;
    action def KeepClearOfOtherVessels;
    action def ReportToVts;
    action def MonitorTraffic;

    // ---------- Operational capability ----------
    use case def TransitTheSolent {
        doc /* Get from one harbour in the Solent to another safely, sharing
             * the water with ferries, large ships and small craft. */
        subject waterway : Waterway;
        actor operator : MissionOperator;
        actor traffic : Vessel[0..*];
        actor vts : VesselTrafficService;
        objective {
            doc /* Arrive at the destination without grounding, without collision
                 * and without breaking the rules OR1-OR5. */
        }
    }

    // Operational context: who shares the water.
    part solent : Waterway {
        part ferries : Ferry[0..*];
        part largeShips : LargeShip[0..*];
        part smallCraft : SmallCraft[0..*];
        part vts : VesselTrafficService;
    }
}
