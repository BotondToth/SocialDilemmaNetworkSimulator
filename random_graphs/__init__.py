import networkx as nx
from networkx import Graph, read_pajek
import matplotlib.pyplot as plt
import random

from plots import FIG_SIZE


def erdos_renyi(n, p=0.15) -> Graph:
    plt.figure(figsize=FIG_SIZE)
    g = nx.Graph()
    g.add_nodes_from(range(n))
    for i in g.nodes():
        for j in g.nodes():
            if i < j:
                _r = random.random()
                if _r < p:
                    g.add_edge(i, j)
    return g


def small_world(n, m, p=0.15) -> Graph:
    return nx.newman_watts_strogatz_graph(n, m, p)


def barabasi_albert_graph(n, m):
    return nx.barabasi_albert_graph(n, m)


def get_graph_from_name(name: str, n, p, m, pajek_path) -> Graph:
    if name == "erdos_renyi":
        return erdos_renyi(n, p)
    if name == "small_world":
        return small_world(n, m, p)
    if name == "barabasi_albert":
        return barabasi_albert_graph(n, m)
    if name == "pajek":
        return read_pajek(pajek_path)
