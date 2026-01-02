from ocelescope import OCEL_FIELD, PluginInput


class DFGInput(PluginInput):
    excluded_event_types: list[str] = OCEL_FIELD(title="Excluded Activities", field_type="event_type", ocel_id="ocel")

    excluded_object_types: list[str] = OCEL_FIELD(
        title="Excluded Object Types", field_type="object_type", ocel_id="ocel"
    )
