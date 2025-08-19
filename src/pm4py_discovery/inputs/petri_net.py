from typing import Literal

from ocelescope import OCEL_FIELD, PluginInput
from pydantic import Field


class PetriNetInput(PluginInput, frozen=True):
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
