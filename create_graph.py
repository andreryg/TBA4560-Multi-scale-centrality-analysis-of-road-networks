import networkx as nx
from download_nvdb_data import gather_road_data
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def create_adjacency_list(road_dataframe):
    """
    Takes a dataframe of road segments and returns a dictionary of adjacency list graph representation.
    """
    adjacency_list = {}

    for ind in road_dataframe.index:

        adj_noder = road_dataframe.loc[((road_dataframe['startnode'] == road_dataframe['startnode'][ind]) | (road_dataframe['sluttnode'] == road_dataframe['startnode'][ind]) | (road_dataframe['startnode'] == road_dataframe['sluttnode'][ind]) | (road_dataframe['sluttnode'] == road_dataframe['sluttnode'][ind]))]
        node_list = adj_noder.index.tolist()
        node_list.remove(ind)

        adjacency_list.update({ind : node_list})

        """if ind == 5:
            break"""

    return adjacency_list

road_data = gather_road_data()
nodes = create_adjacency_list(road_data)
G = nx.Graph(nodes)

nx.draw(G, with_labels=True, font_weight='bold')
plt.show()
