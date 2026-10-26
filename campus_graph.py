
import networkx as nx


campus_graph = nx.Graph()

campus_graph.add_edges_from([
    ("VED226", "VED329", {"distance": 30}),
    ("VED329", "VED505", {"distance": 40}),
    ("VED226", "VED505", {"distance": 60})
])


def shortest_route(start_room, destination_room):
    if start_room not in campus_graph:
        return None, None

    if destination_room not in campus_graph:
        return None, None

    route = nx.shortest_path(
        campus_graph,
        source=start_room,
        target=destination_room,
        weight="distance"
    )

    distance = nx.shortest_path_length(
        campus_graph,
        source=start_room,
        target=destination_room,
        weight="distance"
    )

    return route, distance
