from ocelescope import Resource, Table, TableColumn


class TokenBasedReplayResult(Resource):
    produced: int
    consumed: int
    remaining: int
    missing: int

    def visualize(self) -> Table:
        return Table(
            columns=[
                TableColumn(id="category", label="Category", data_type="string"),
                TableColumn(id="value", label="Value", data_type="number"),
            ],
            rows=[
                {"category": "Produced", "value": self.produced},
                {"category": "Consumed", "value": self.consumed},
                {"category": "Remaining", "value": self.remaining},
                {"category": "Missing", "value": self.missing},
            ],
        )
