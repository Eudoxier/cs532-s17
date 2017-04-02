#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" kgraph.py

Create a graph of the Zachary Karate Club data.

* Original Paper: http://aris.ss.uci.edu/~lin/76.pdf

"""

try:
    import pylab as plt
    import networkx as nx
except ImportError as e:
    print("[*] Error: {}".format(e))
    print("[*] Please run `pip install -r requrements.txt` before using this program.")
    sys.exit(1)

__author__ = "Derek Goddeau"

class Kclub():
    """ A representation of Zachery's Karete Club.

    """
    def __init__(self):
        self.G = None
        self.heavy = []
        self.mid = []
        self.lite = []
        self.max_weight = None
        self.node_size = []
        self.mr_hi_labels = {}
        self.officer_labels = {}
        self.edge_cmap = plt.cm.viridis
        self.graph_bkgrd = '#333333'
        self.label_color = '#8e89a5'

    def graph(self):
        """

        """
        self.get_data()
        self.analyse_data()
        self.graph_data()


    def get_data(self):
        """

        """
        # Use the data available from NetworkX
        self.G = nx.karate_club_graph()

        with open('connection_matrix.dat', 'r') as datfile:
            data = []
            for line in datfile:
                data.append(max(line))

            self.max_weight = float(max(data))


        # Get weight values
        # Todo: add data to class
        with open('connection_matrix.dat', 'r') as datfile:
            
            # Generate a list of lists 
            # Each with the connection strength
            lines = []
            for line in datfile:
                lines.append(line.split())
            
            # Enumerate to get the data encoded by index
            # The index of each item per line represents
            # The connected node
            for line in enumerate(lines):
                lines[line[0]] = list(enumerate(line[1]))
                
            # Enter the data in the graph
            for line in enumerate(lines):
                strength={}
                for connection in line[1]:
                    if int(connection[1]) is not 0:
                        node=connection[0]
                        weight=float(connection[1])
                        norm_weight=float(weight)/self.max_weight
                        self.G.add_edge(line[0], node, weight=weight, norm_weight=norm_weight)




    def analyse_data(self):
        """

        """
        # Node degree info
        node_degrees = [ self.G.degree()[node] for node in self.G.nodes() ]
        node_degrees_norm = [ node_degree/max(node_degrees) for node_degree in node_degrees]
        self.node_size = [ node_degree*3000 for node_degree in node_degrees_norm ]

        # Split the node labels into categories based on group
        for node in self.G.nodes(data=True):
            if node[1]['club'] == 'Mr. Hi':
                self.mr_hi_labels.update({node[0]: node[0]})
            if node[1]['club'] == 'Officer':
                self.officer_labels.update({node[0]: node[0]})

        # Split the edges into categories based on weight
        self.heavy = [(u,v) for (u,v,d) in self.G.edges(data=True) if d['norm_weight'] > 0.66]
        self.mid = [(u,v) for (u,v,d) in self.G.edges(data=True) if d['norm_weight'] <= 0.66 and d['norm_weight'] > 0.33 ]
        self.lite = [(u,v) for (u,v,d) in self.G.edges(data=True) if d['norm_weight'] <= 0.33]


    def graph_data(self):
        """

        """
        # Get the data for edge colors
        edges = self.G.edges()
        edge_weights = [ self.G[source][dest]['weight'] for source, dest in edges ]
        edge_color = [ self.edge_cmap(weight/self.max_weight) for weight in edge_weights ]

        # Color bar setup
        plt.ioff() # Don't do anything while setting up scale
        colors_unscaled = [ tuple(map(lambda x: self.max_weight*x, y)) for y in edge_color ]
        heatmap = plt.pcolor(colors_unscaled, cmap=self.edge_cmap)
        plt.close()

        # Re-map the colors
        heavy_edge_weights = [ self.G[source][dest]['weight'] for source, dest in self.heavy ]
        heavy_edge_color = [ self.edge_cmap(weight/self.max_weight) for weight in heavy_edge_weights ]
        mid_edge_weights = [ self.G[source][dest]['weight'] for source, dest in self.mid ]
        mid_edge_color = [ self.edge_cmap(weight/self.max_weight) for weight in mid_edge_weights ]
        lite_edge_weights = [ self.G[source][dest]['weight'] for source, dest in self.lite ]
        lite_edge_color = [ self.edge_cmap(weight/self.max_weight) for weight in lite_edge_weights ]

        # Node colormap
        node_color_map = {'Mr. Hi': self.graph_bkgrd, 'Officer': self.label_color}
        node_colors = [ node_color_map[self.G.node[node]['club']] for node in self.G ]

        # Graph everything seperate
        fig, axes = plt.subplots(1,1, figsize=(14,9), dpi=300, frameon=False)
        pos = nx.nx_pydot.graphviz_layout(self.G,prog="neato", root=33)
        nx.draw_networkx_nodes(self.G, pos, node_color=node_colors, node_size=self.node_size,
                               with_labels=True, ax = axes, linewidths=1)
        nx.draw_networkx_labels(self.G, pos, labels=self.mr_hi_labels, font_color=self.label_color)
        nx.draw_networkx_labels(self.G, pos, labels=self.officer_labels, font_color=self.graph_bkgrd)
        nx.draw_networkx_edges(self.G, pos, edgelist=self.heavy, edge_color=heavy_edge_color, width=3)
        nx.draw_networkx_edges(self.G, pos, edgelist=self.mid, edge_color=mid_edge_color, width=3, style='dashed')
        nx.draw_networkx_edges(self.G, pos, edgelist=self.lite, edge_color=lite_edge_color, width=3, style='dotted')

        # Get rid of boundaries
        axes.get_xaxis().set_visible(False)
        axes.get_yaxis().set_visible(False)
        plt.axis('off')

        # colorbar
        cbar = plt.colorbar(heatmap)
        cbar.ax.set_ylabel('edge weight',labelpad=15,rotation=270)

        plt.show()

if __name__ == "__main__":
    k = Kclub()
    k.graph()
