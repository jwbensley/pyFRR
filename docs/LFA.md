# Loop Free Alternatives


### LFA Details


   In general, to be able to calculate the set of LFAs for a specific
   destination D, the source router S needs to know the following basic pieces
   of information:

   o  Shortest-path distance from the calculating router to the
      destination (Distance_opt(S, D))

   o  Shortest-path distance from the router's IGP neighbors to the
      destination (Distance_opt(N, D))

   o  Shortest path distance from the router's IGP neighbors to itself
      (Distance_opt(N, S))

   o  Distance_opt(S, D) is normally available from the regular SPF
      calculation performed by the link-state routing protocols.
      Distance_opt(N, D) and Distance_opt(N, S) can be obtained by
      performing additional SPF calculations from the perspective of
      each IGP neighbor (i.e., considering the neighbor's vertex as the
      root of the SPT (SPT(N) rather than SPT(S)).


LFA only provides protection against a single link failure between S and it's directly connceted neighbour N, the next-hop towards D, or the directly connect neighbour N itself. If a 2nd failure occurs it is possible for a mico-loop to occure until the IGP has converged.

  A neighbor N can provide a loop-free alternate (LFA) if and only if

        Distance_opt(N, D) < Distance_opt(N, S) + Distance_opt(S, D)

                     Inequality 1: Loop-Free Criterion

   A subset of loop-free alternates are downstream paths that must meet
   a more restrictive condition that is applicable to more complex
   failure scenarios:

                 Distance_opt(N, D) < Distance_opt(S, D)

                  Inequality 2: Downstream Path Criterion




Node-Protecting Alternate Next-Hops

   For an alternate next-hop N to protect against node failure of a
   primary neighbor E for destination D, N must be loop-free with
   respect to both E and D.  In other words, N's path to D must not go
   through E.  This is the case if Inequality 3 is true, where N is the
   neighbor providing a loop-free alternate.

         Distance_opt(N, D) < Distance_opt(N, E) + Distance_opt(E, D)

     Inequality 3: Criteria for a Node-Protecting Loop-Free Alternate

   If Distance_opt(N,D) = Distance_opt(N, E) + Distance_opt(E, D), it is
   possible that N has equal-cost paths and one of those could provide
   protection against E's node failure.  However, it is equally possible
   that one of N's paths goes through E, and the calculating router has
   no way to influence N's decision to use it.  Therefore, it SHOULD be
   assumed that an alternate next-hop does not offer node protection if
   Inequality 3 is not met.



   If the primary next-hop uses a broadcast link, then an alternate
   SHOULD be loop-free with respect to that link's pseudo-node (PN) to
   provide link protection.  This requirement is described in Inequality
   4 below.

              D_opt(N, D) < D_opt(N, PN) + D_opt(PN, D)

   Inequality 4: Loop-Free Link-Protecting Criterion for Broadcast Links






   When calculating alternate next-hops, the calculating router S
   applies the following rules.

   1.  S SHOULD select a loop-free node-protecting alternate next-hop,
       if one is available.  If no loop-free node-protecting alternate
       is available, then S MAY select a loop-free link-protecting
       alternate.

   2.  If S has a choice between a loop-free link-and-node-protecting
       alternate and a loop-free node-protecting alternate that is not
       link-protecting, S SHOULD select a loop-free link-and-node-
       protecting alternate.  This can occur as explained in
       Section 3.3.

   3.  If S has multiple primary next-hops, then S SHOULD select as a
       loop-free alternate either one of the other primary next-hops or
       a loop-free node-protecting alternate if available.  If no loop-
       free node-protecting alternate is available and no other primary
       next-hop can provide link-protection, then S SHOULD select a
       loop-free link-protecting alternate.

   4.  Implementations SHOULD support a mode where other primary next-
       hops satisfying the basic loop-free condition and providing at
       least link or node protection are preferred over any non-primary
       alternates.  This mode is provided to allow the administrator to
       preserve traffic patterns based on regular ECMP behavior.

   5.  Implementations considering SRLGs MAY use SRLG protection to
       determine that a node-protecting or link-protecting alternate is
       not available for use.
       
   Primary Path -  The next-hop is used by S as primary.

   Loop-Free Node-Protecting Alternate -  This next-hop satisfies
      Inequality 1 and Inequality 3.  The path avoids S, S's primary
      neighbor E, and the link from S to E.

   Loop-Free Link-Protecting Alternate -  This next-hop satisfies
      Inequality 1 but not Inequality 3.  If the primary next-hop uses a
      broadcast link, then this next-hop satisfies Inequality 4.
