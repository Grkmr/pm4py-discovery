from typing import Annotated

import pm4py
from ocelescope import (
    OCEL,
    DirectlyFollowsGraph,
    EventTypeFilter,
    ObjectTypeFilter,
    OCELAnnotation,
    PetriNet,
    Plugin,
    plugin_method,
)

from .inputs.dfg import DFGInput
from .inputs.petri_net import PetriNetInput
from .util.dfg import compute_ocdfg
from .util.petri_net import convert_flat_pm4py_to_ocpn


class Pm4pyDiscovery(Plugin):
    label = "PM4PY Discovery"
    description = "A plugin to discover object centric process models using the pm4py python library"
    version = "1.0"

    @plugin_method(label="Discover Petri net", description="Discover a object-centric petri net")
    def petri_net(
        self,
        ocel: Annotated[OCEL, OCELAnnotation(label="Event Log")],
        input: PetriNetInput,
    ) -> PetriNet:
        filtered_ocel = ocel.apply_filter(
            filters={
                "event_type": EventTypeFilter(event_types=input.excluded_event_types, mode="exclude"),
                "object_types": ObjectTypeFilter(object_types=input.excluded_object_types, mode="exclude"),
            }
        )
        petri_net = pm4py.discover_oc_petri_net(
            inductive_miner_variant=input.variant,
            ocel=filtered_ocel.ocel,
            diagnostics_with_tbr=input.enable_token_based_replay,
        )

        petri_net = convert_flat_pm4py_to_ocpn(petri_net["petri_nets"])

        return petri_net

    @plugin_method(
        label="Discover Directly Follows Graph",
        description="Discover a object-centric directly follows graph",
    )
    def directly_follows_graph(
        self, ocel: Annotated[OCEL, OCELAnnotation(label="Event Log")], input: DFGInput
    ) -> DirectlyFollowsGraph:
        filtered_ocel = ocel.apply_filter(
            filters={
                "event_type": EventTypeFilter(event_types=input.excluded_event_types, mode="exclude"),
                "object_types": ObjectTypeFilter(object_types=input.excluded_object_types, mode="exclude"),
            }
        )
        return compute_ocdfg(filtered_ocel)
