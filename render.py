import networkx as nx
import matplotlib.pyplot as plt
import json

# g = nx.Graph()
g_data = json.load(open("examples/mesh/mesh.json"))
g = nx.readwrite.json_graph.node_link_graph(g_data)
nx.draw(g, with_labels=True)
plt.savefig("filename.png")
