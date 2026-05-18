class ParsingTableSerializer:

    #
    # ==========================================================
    # LR
    # ==========================================================
    #

    @staticmethod
    def serialize_lr(parser):

        return {

            "action": [

                {
                    "state": state,

                    "symbol": symbol,

                    "actions":
                        sorted(
                            list(actions)
                        )
                }

                for (
                    state,
                    symbol
                ), actions

                in sorted(
                    parser.action_table.items()
                )
            ],

            "goto": [

                {
                    "state": state,

                    "symbol": symbol,

                    "target": target
                }

                for (
                    state,
                    symbol
                ), target

                in sorted(
                    parser.goto_table.items()
                )
            ]
        }

    #
    # ==========================================================
    # LL1
    # ==========================================================
    #

    @staticmethod
    def serialize_ll1(parser):

        return [

            {
                "non_terminal":
                    non_terminal,

                "terminal":
                    terminal,

                "productions": [

                    str(production)

                    for production
                    in productions
                ]
            }

            for (
                non_terminal,
                terminal
            ), productions

            in sorted(
                parser.parsing_table.items()
            )
        ]