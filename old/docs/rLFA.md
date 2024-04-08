
### Usage

The rLFA class returns the best rFLA path (meaning lowest cost)  or multiple rFLA paths if multiple paths are tied (multiple equal cost best paths. The process on weather to use multiple rFLAs and load-balance over them (i.e., to reduce congestion during a failure scenario) or to use a single path is out of the scope of this class. The class returns all paths so that your own logic can be implemented for chosen on or multiple rFLA paths.



   Repair tunnel:
      A tunnel established for the purpose of providing a virtual
      neighbor that is a Loop-Free Alternate.

   P-space:
      The P-space of a router with respect to a protected link is the
      set of routers reachable from that specific router using the pre-
      convergence shortest paths without any of those paths (including
      equal-cost path splits) transiting that protected link.

      For example, the P-space of S with respect to link S-E is the set
      of routers that S can reach without using the protected link S-E.

   Extended P-space:
      Consider the set of neighbors of a router protecting a link.
      Exclude from that set of routers the router reachable over the
      protected link.  The extended P-space of the protecting router
      with respect to the protected link is the union of the P-spaces of
      the neighbors in that set of neighbors with respect to the
      protected link (see Section 5.2.1.2).

   Q-space:
      The Q-space of a router with respect to a protected link is the
      set of routers from which that specific router can be reached
      without any path (including equal-cost path splits) transiting
      that protected link.

   PQ node:
      A PQ node of a node S with respect to a protected link S-E is a
      node that is a member of both the P-space (or the extended
      P-space) of S with respect to that protected link S-E and the
      Q-space of E with respect to that protected link S-E.  A repair
      tunnel endpoint is chosen from the set of PQ-nodes.

   Remote LFA (RLFA):
      The use of a PQ node rather than a neighbor of the repairing node
      as the next hop in an LFA repair [RFC5286].


        """
           The properties that are required of repair tunnel endpoints are as
           follows:

           o  The repair tunneled point MUST be reachable from the tunnel source
              without traversing the failed link; and

           o  when released from the tunnel, packets MUST proceed towards their
              destination without being attracted back over the failed link.
        """





RFC7490:
```
   RFC 5714 [RFC5714] describes a framework for IP Fast Reroute (IPFRR)
   and provides a summary of various proposed IPFRR solutions.  A basic
   mechanism using Loop-Free Alternates (LFAs) is described in [RFC5286]
   that provides good repair coverage in many topologies [RFC6571],
   especially those that are highly meshed.  However, some topologies,
   notably ring-based topologies, are not well protected by LFAs alone.
   This is because there is no neighbor of the Point of Local Repair
   (PLR) that has a cost to the destination via a path that does not
   traverse the failure that is cheaper than the cost to the destination
   via the failure.

   The method described in this document extends the LFA approach
   described in [RFC5286] to cover many of these cases by tunneling the
   packets that require IPFRR to a node that is both reachable from the
   PLR and can reach the destination.



The p space is the area of the network within which a packet can be transmitted towards a specific destination without the packet being reflected back to the forwarding router. If a packet is forwarded into the q space, however, it will be forwarded back in a loop. The key point is, then, to find someplace in the q space where the packet can be forwarded without the packet being looped back to the sender.


(the repair tunnel endpoint) is a "PQ node",
```