from typing import Any, Optional
from networkx import Graph
import networkx as nx


def read_pajek(path: str) -> Any:
    return nx.read_pajek(path)


def write_pajek(_g: Graph, path: str) -> Optional[Any]:
    return nx.write_pajek(_g, path)
