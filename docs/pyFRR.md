# pyFRR Module

Using this module can be broken down in to three losely coupled steps:

* Provide some input topology data in one of a variety of formats

* Generate the paths you want (SPF/LFA/rFLA/TI-LFA)

* Retrieve the output in one of a variety of formats


## Input topology data

Topology data can be provided to the module in a variety of formats. The module is always initiated with topology data passed at init. At init the module parses the topology data and generates a unidirectional NetworkX graph object. This graph object is the basis for all calculations subsequently performed.

One should add the weight key-value to link/edge data if it isn't included in the export from your network devices or OSS stack. This module is based on link costs, not hop count. What type of metric used is abitrary (delay, utilisation, speed, etc.) as long as it is an integer.

Regardless of what label is included in the imported data, the module will render graphs using the link/edge weight as it's label text.

For nodes the node id or name is used as it's label text by default in rendered diagrams. Including a `label` field in the input data will override this node label in rendered diagrams.

It is assumed that all topology information being processed is within the same IGP area / routing domain, thus all links are equally viable for use due to inter-area or inter-AS limits (except for their weight/cost).


### Loading an existing NetworkX graph

If you already have your network topology available as a NetworkX graph, simply pass that to the module when you instantiate it:

```python
$ python3

>>> import networkx as nx
>>> G = nx.Graph()
>>> G.add_nodes_from([1, 2, 3])
>>> G.add_edges_from([(1, 2), (2, 3), (3, 1)])
>>>
>>> import pyfrr
>>> f = pyfrr.pyfrr(graph=G)
>>> f.graph.nodes
NodeView((1, 2, 3))
```

### Load a topology file

The module currently supports loading a JSON or dot file. The filename AND file type must be specified. The module will load the file contents and create a networkX graph from the topology data in the file.

Below is a JSON example. The JSON file must contain the two lists of arrays, `nodes` and `links`. You should easily be able to pull your topology in the required JSON format from your OSS stack, which definately as an API right? ;)

```python
$ python3

>>> import pyfrr
>>> kwargs = { "filename": "example/mesh_topo.json", "filetype": "json" }
>>> f = pyfrr.pyfrr(**kwargs)
>>> f.graph.nodes
NodeView(('P1', 'P2', 'P3', 'P4', 'PE1', 'PE2', 'PE3', 'PE4', 'PE5'))
```

Below is a dot example. In this example the IS-IS topology is pulled from a router in a lab running IOS-XR, which is able to dump the IS-IS database in DOT format on the CLI.

```
RP/0/RP0/CPU0:xrv9k-2#show isis database graph verbose 
Tue Apr 27 09:29:10.089 UTC

/*
 * Network topology in DOT format. For information on using this to
 * generate graphical representations see http://www.graphviz.org
 */
digraph "level-2" {
  graph [rankdir=LR];
  node [fontsize=9];
  edge [fontsize=6];
  "xrv9k-1" [label="\N\n192.0.2.1"];
  "xrv9k-2" [label="\N\n192.0.2.2"];
  "e3" [label="\N\n192.0.2.3"];
  "e4" [label="\N\n192.0.2.4"];
  "j5" [label="\N\n192.0.2.5"];
  "j6" [label="\N\n192.0.2.6"];
}
```
This dot data is saved to a file for use with this module.

```python
$ python3

>>> import pyfrr
>>> kwargs = { "filename": "example/lab_topo.dot", "filetype": "dot" }
>>> f = pyfrr.pyfrr(**kwargs)
>>> f.graph.nodes
NodeView(('xrv9k-1', 'xrv9k-2', 'e3', 'e4', 'j5', 'j6'))
>>> f.graph.edges
EdgeView([('xrv9k-1', 'xrv9k-2'), ('xrv9k-1', 'j6'), ('xrv9k-2', 'e3'), ('e3', 'e4'), ('e4', 'j5'), ('j5', 'j6')])
```

### Passing raw data

One can pass the list of links and nodes directly to the module when it is instantiated:

```bash
python3

>>> import pyfrr
>>> nodes = [
    {"id": "R1"},
    {"id": "R2"},
    {"id": "R3"}
]
>>> links = [
    {"source": "R1", "target": "R2", "weight": 10},
    {"source": "R2", "target": "R3", "weight": 10},
    {"source": "R3", "target": "R1", "weight": 10}
]
>>> f = pyfrr.pyfrr(links=links, nodes=nodes)
>>> f.graph.nodes
NodeView(('R1', 'R2', 'R3'))
```

## Calculating paths

There is a parent method for each type of supported path calculation e.g., LFA or SPF, which calculates all paths in the network graph of that type. The results of the calculation are stored in a series of nested dicts keyed by source, then  destination, then path type.


## Raw paths

Below all rFLA paths are calculated, the raw results for any link protecting rLFA paths between PE1 and PE3 are then shown:

```python
$ python3

>>> import pyfrr
>>> kwargs = { "filename": "example/mesh_topo.json", "filetype": "json" }
>>> f = pyfrr.pyfrr(**kwargs)
>>> f.gen_all_metric_rlfas()
>>> f.topo["PE1"]["PE5"]["rlfas_link"]
[([['PE1', 'P1']], [['P1', 'P2', 'PE5']])]
```
## Module functions

`get_paths()` provides a simple wrapper around the results dict. It will return all paths from a given source, or all paths to a given destination, or all paths between a specific source and destination node pair:

```python
$ python3

>>> import pyfrr
>>> kwargs = { "filename": "example/mesh_topo.json", "filetype": "json" }
>>> f = pyfrr.pyfrr(**kwargs)
>>> f.gen_all_metric_rlfas()
>>> f.get_paths(src="PE1")
>>> f.get_paths(dst="PE1")
>>> f.get_paths(src="PE1", dst="PE5")
{'cost': [], 'lfas_dstream': [], 'lfas_link': [], 'lfas_node': [], 'rlfas_link': [([['PE1', 'P1']], [['P1', 'P2', 'PE5']])], 'rlfas_node': [], 'tilfa_link': [], 'tilfa_node': []}
```

Taking a node down for maintenance and want to know which paths use that node? Use `get_paths_via()`.

In order to see all aftect paths you'd need to first call all the path generating functions for all of the path types in use in your network, so as a minimum `pyfrr.gen_all_metric_spts()` then any of `pyfrr.gen_all_metric_lfas()`, `pyfrr.gen_all_metric_rlfas()`, `pyfrr.get_all_metric_tilfas()`. Then call `get_paths_via()` to see if any of these paths traverse the maintenance node.

Below it can be seen that the rLFA link protecting paths from P3 to P2, P4 and PE1 all go via P1.

```python
$ python3

>>> import pyfrr
>>> kwargs = { "filename": "example/mesh_topo.json", "filetype": "json" }
>>> f = pyfrr.pyfrr(**kwargs)
>>> f.gen_all_metric_rlfas()
>>> f.get_paths_via(via="P1")
{'P3': {'P2': {'rlfas_link': [['P3', 'PE3', 'P1', 'P2']]}, 'P4': {'rlfas_link': [['P3', 'P1', 'PE1', 'P2', 'P4']]}, 'PE1': {'rlfas_link': [['P3', 'PE3', 'P1', 'PE1']]}}, 'P4': {'P2': {'rlfas_link': [['P4', 'P3', 'PE3', 'P1', 'P2']]}, 'P3': {'rlfas_link': [['P4', 'P2', 'PE1', 'P1', 'P3']]}, 'PE1': {'rlfas_link': [['P4', 'P3', 'P1', 'PE1']], 'rlfas_node': [['P4', 'P3', 'P1', 'PE1']]}, 'PE3': {'rlfas_link': [['P4', 'P2', 'P1', 'PE3']], 'rlfas_node': [['P4', 'P2', 'P1', 'PE3']]}}, 'PE2': {'P2': {'rlfas_link': [['PE2', 'P3', 'P1', 'P2']]}, 'PE1': {'rlfas_link': [['PE2', 'P3', 'PE3', 'P1', 'PE1']], 'rlfas_node': [['PE2', 'P3', 'PE3', 'P1', 'PE1']]}}, 'PE3': {'P2': {'rlfas_link': [['PE3', 'P3', 'P1', 'P2']]}, 'PE1': {'rlfas_link': [['PE3', 'P3', 'P1', 'PE1']]}, 'PE4': {'rlfas_link': [['PE3', 'P1', 'PE1', 'P2', 'PE4']], 'rlfas_node': [['PE3', 'P1', 'PE1', 'P2', 'PE4']]}, 'PE5': {'rlfas_link': [['PE3', 'P1', 'PE1', 'P2', 'PE5']], 'rlfas_node': [['PE3', 'P1', 'PE1', 'P2', 'PE5']]}}, 'P2': {'P3': {'rlfas_link': [['P2', 'PE1', 'P1', 'P3']]}, 'P4': {'rlfas_link': [['P2', 'P1', 'PE3', 'P3', 'P4']]}, 'PE3': {'rlfas_link': [['P2', 'PE1', 'P1', 'PE3']]}}, 'PE1': {'P3': {'rlfas_link': [['PE1', 'P2', 'P1', 'P3']]}, 'PE2': {'rlfas_link': [['PE1', 'P1', 'PE3', 'P3', 'PE2']], 'rlfas_node': [['PE1', 'P1', 'PE3', 'P3', 'PE2']]}, 'PE3': {'rlfas_link': [['PE1', 'P2', 'P1', 'PE3']]}}, 'PE4': {'P3': {'rlfas_link': [['PE4', 'P2', 'P1', 'P3']]}, 'PE3': {'rlfas_link': [['PE4', 'P2', 'PE1', 'P1', 'PE3'], ['PE4', 'P2', 'PE5', 'P2', 'P1', 'PE3'], ['PE4', 'P4', 'PE5', 'P2', 'P1', 'PE3']], 'rlfas_node': [['PE4', 'P2', 'PE1', 'P1', 'PE3']]}}, 'PE5': {'P3': {'rlfas_link': [['PE5', 'P2', 'P1', 'P3']]}, 'PE3': {'rlfas_link': [['PE5', 'P2', 'PE1', 'P1', 'PE3'], ['PE5', 'P2', 'PE4', 'P2', 'P1', 'PE3'], ['PE5', 'P4', 'PE4', 'P2', 'P1', 'PE3']], 'rlfas_node': [['PE5', 'P2', 'PE1', 'P1', 'PE3']]}}}
```


