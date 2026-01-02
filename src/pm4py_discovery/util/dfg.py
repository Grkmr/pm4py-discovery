import pm4py
from ocelescope import OCEL, DirectlyFollowsGraph
from ocelescope.resource.default.dfg import (
    DFGActivity,
    DFGEdge,
    DFGObject,
)


def compute_ocdfg(ocel: OCEL) -> DirectlyFollowsGraph:
    ocdfg = pm4py.discover_ocdfg(ocel.ocel)

    edge_count_dict = {}
    for object_type, values in ocdfg["edges"]["event_couples"].items():
        for key, events in values.items():
            edge_count_dict[(object_type, key)] = len(events)

    edges = []
    for object_type, raw_edges in ocdfg["edges"]["event_couples"].items():
        edges = edges + (
            [
                DFGEdge(
                    object_type=object_type,
                    source=source,
                    target=target,
                )
                for source, target in raw_edges
            ]
        )

    start_activity_edges = [
        DFGEdge(
            object_type=object_type,
            source=activity,
        )
        for object_type, activities in ocdfg["start_activities"]["events"].items()
        for activity in activities.keys()
    ]

    end_activity_edges = [
        DFGEdge(
            source=activity,
            object_type=object_type,
        )
        for object_type, activities in ocdfg["end_activities"]["events"].items()
        for activity in activities.keys()
    ]

    return DirectlyFollowsGraph(
        activities=[DFGActivity(name=activity) for activity in ocdfg["activities"]],
        edges=edges + start_activity_edges + end_activity_edges,
        object_types=[DFGObject(name=object_type) for object_type in ocdfg["object_types"]],
    )
