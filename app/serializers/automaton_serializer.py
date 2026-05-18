class AutomatonSerializer:

    @staticmethod
    def serialize(automaton):

        return {

            "states": [

                {
                    "id": state.id,

                    "items": [

                        str(item)

                        for item
                        in sorted(
                            state.items,
                            key=str
                        )
                    ]
                }

                for state
                in sorted(
                    automaton.states.values(),
                    key=lambda s: s.id
                )
            ],

            "transitions": [

                {
                    "source":
                        transition.source_id,

                    "target":
                        transition.target_id,

                    "symbol":
                        transition.symbol
                }

                for transition
                in sorted(
                    automaton.transitions,
                    key=lambda t: (
                        t.source_id,
                        t.target_id,
                        t.symbol
                    )
                )
            ]
        }