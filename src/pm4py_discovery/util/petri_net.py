from dataclasses import dataclass
from typing import Literal

from ocelescope import PetriNet
from ocelescope.plugin import OCEL_FIELD, PluginInput
from ocelescope.resource.default.petri_net import Arc, Place, Transition
from pm4py.objects.petri_net.obj import PetriNet as PMNet
from pydantic.fields import Field

from ..resources import TokenBasedReplayResult


class PetriNetInput(PluginInput):
    variant: Literal["im", "imd"] = Field(
        title="Mining Variant",
        description="Variant of the inductive miner to use (“im” for traditional;"
        "“imd” for the faster inductive miner directly-follows).",
    )
    enable_token_based_replay: bool = Field(
        default=False,
        title="Enable Token Based Replay",
        description="Enable the computation of diagnostics using token-based replay.",
    )
    excluded_event_types: list[str] = OCEL_FIELD(title="Excluded Activities", field_type="event_type", ocel_id="ocel")

    excluded_object_types: list[str] = OCEL_FIELD(
        title="Excluded Object Types", field_type="object_type", ocel_id="ocel"
    )


@dataclass
class TBRResult:
    place_results: dict[tuple[str, str], TokenBasedReplayResult]
    arc_results: dict[tuple[str, str], int]


def extract_tbr_results(tbr_results: dict[str, tuple[dict, dict]]) -> TBRResult:
    place_results: dict[tuple[str, str], TokenBasedReplayResult] = {}
    arc_results: dict[tuple[str, str], int] = {}

    for object_type, place_result in tbr_results.items():
        place_results = place_results | {
            (object_type, place_name.name): TokenBasedReplayResult(
                produced=tbr_dict["p"], consumed=tbr_dict["c"], remaining=tbr_dict["r"], missing=tbr_dict["m"]
            )
            for place_name, tbr_dict in place_result[0].items()
        }

        arc_results = arc_results | {
            (object_type, transition.label if transition.label else transition.name): sync_moves
            for transition, sync_moves in place_result[1].items()
        }

    return TBRResult(place_results=place_results, arc_results=arc_results)


def convert_flat_pm4py_to_ocpn(flat_nets: dict[str, PMNet], tbr_results: TBRResult | None = None) -> PetriNet:
    place_set: list[Place] = []
    transition_map: dict[str, Transition] = {}
    arcs: list[Arc] = []

    tbr_results = tbr_results or TBRResult(place_results={}, arc_results={})

    seen_places: set[str] = set()

    for object_type, pm_net in flat_nets.items():
        pm_net = pm_net[0]  # type:ignore

        for place in pm_net.places:
            qualified_id = f"{object_type}_{place.name}"
            if qualified_id not in seen_places:
                place_set.append(
                    Place(
                        id=qualified_id,
                        place_type="source" if place.name == "source" else "sink" if place.name == "sink" else None,
                        object_type=object_type,
                        annotation=tbr_results.place_results.get((object_type, place.name), None),
                    )
                )
                seen_places.add(qualified_id)

        for transition in pm_net.transitions:
            label = transition.label or transition.name
            if label not in transition_map:
                transition_map[label] = Transition(
                    id=label,
                    label=transition.label,
                )

        for arc in pm_net.arcs:
            source_id = arc.source.name if isinstance(arc.source, PMNet.Place | PMNet.Transition) else str(arc.source)
            target_id = arc.target.name if isinstance(arc.target, PMNet.Place | PMNet.Transition) else str(arc.target)

            # Adjust for qualified place IDs
            if isinstance(arc.source, PMNet.Place):
                source_id = f"{object_type}_{source_id}"
            if isinstance(arc.target, PMNet.Place):
                target_id = f"{object_type}_{target_id}"

            # If transition, map to unified label
            if isinstance(arc.source, PMNet.Transition):
                source_id = arc.source.label or arc.source.name
            if isinstance(arc.target, PMNet.Transition):
                target_id = arc.target.label or arc.target.name

            arcs.append(
                Arc(
                    source=source_id,
                    target=target_id,
                )
            )

    # Assemble the final Petri net and OCPN
    return PetriNet(
        places=place_set,
        transitions=list(transition_map.values()),
        arcs=arcs,
    )
