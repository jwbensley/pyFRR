
# WIP: TI-LFA IS A WIP AND NOT YET FINISHED!

## Overview

The TI-LFA module tries to calculate the lowest cost path from the source node to the destination node, avoid the failed first hop link(s) or node(s). Like the LFA and rLFA modules, the pre-failure best path could be a single path, and when that is unavailable there could be multiple paths tied for the 2nd lowest cost path between source and destination nodess (ECMP). The reverse situation is also possible, the lowest cost path pre-failure is two or more ECMP paths an afer they have all failed the next best path post-failure may be a single path. This means that the calculated TI-LFA path may route traffic from a single failed path over multiple ECMP backup paths, or that traffic from multiple best paths is routed post-failure over a single backup path. Equally there may be multiple best paths and multiple 2nd best paths meaning that after all paths in a set of ECMP paths have failed traffic is routed over a different set of ECMP paths.

The TI-LFA module initially choses the lowest cost post-failure path(s) to protect the failued best path(s). This is based on metric/cost. There can be many backup ECMP paths which weren't possible when using LFA or rFLA, which can take crazy paths all over the network due to using only a single metric value (such as only bandwidth or only latency). You need to feed in whatever metric is more important to you. The TI-LFA module then reduces the TI-LFA candidate list by choosing the lowest cost backup paths which also require the fewest number of SIDs to reduce the number of SIDs that need to be included. As a generalisation, the larger the stack of SIDs required, the more indirect the backup path. This avoids longer more indirect paths, which despite having an equal cost as other backup paths, are probably undesired.

### Limitations

FlexAgo for Prefix-SIDs is not supported. If a path from the repair node to the destination node is modified by a local policy on a node (e.g., a constrained path which isn't the default shortest path is applied to the destination node's "Node-SID" [a Prefix-SID]), that path is ignored, only the default shortest path is evaluated by this module.

