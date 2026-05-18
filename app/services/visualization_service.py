from app.serializers.automaton_serializer import (
    AutomatonSerializer
)

from app.serializers.parsing_table_serializer import (
    ParsingTableSerializer
)

from app.serializers.trace_serializer import (
    TraceSerializer
)

from app.serializers.syntax_tree_serializer import (
    SyntaxTreeSerializer
)

from app.viewmodels.automaton_vm import (
    AutomatonViewModel
)

from app.viewmodels.parsing_table_vm import (
    ParsingTableViewModel
)


class VisualizationService:

    #
    # ==========================================================
    # BUILD PARSER VISUALIZATION
    # ==========================================================
    #

    @staticmethod
    def build_parser_visualization(parser):

        data = {

            #
            # parser
            #

            "parser_type":
                parser.__class__.__name__.lower(),

            #
            # grammar
            #

            "grammar": {

                "productions": [

                    str(production)

                    for production
                    in parser.grammar.productions
                ],

                "terminals": sorted(
                    list(
                        parser.grammar.terminals
                        | {"$"}
                    )
                ),

                "non_terminals": sorted(
                    list(
                        parser.grammar.non_terminals
                    )
                ),

                "start_symbol":
                    parser.grammar.start_symbol
            },

            #
            # automata
            #

            "automata": {

                #
                # LL1 => null
                #

                "nfa": None,

                "dfa": None
            },

            #
            # tables
            #

            "tables": {

                #
                # LR
                #

                "action_table": {},

                "goto_table": {},

                #
                # LL1
                #

                "ll1_table": {}
            },

            #
            # sets
            #

            "first_sets": {},

            "follow_sets": {},

            #
            # conflicts
            #

            "conflicts": [],

            #
            # statistics
            #

            "statistics": {

                "num_states": 0,

                "is_valid":

                    parser.is_valid
                    if hasattr(
                        parser,
                        "is_valid"
                    )

                    else True
            }
        }

        #
        # ======================================================
        # LR AUTOMATA
        # ======================================================
        #

        if hasattr(parser, "dfa"):

            #
            # DFA
            #

            dfa_data = (

                AutomatonSerializer
                .serialize(
                    parser.dfa
                )
            )

            data["automata"][
                "dfa"
            ] = (

                AutomatonViewModel
                .build(
                    dfa_data
                )
            )

            #
            # NFA
            #

            nfa_data = (

                AutomatonSerializer
                .serialize(
                    parser.nfa
                )
            )

            data["automata"][
                "nfa"
            ] = (

                AutomatonViewModel
                .build(
                    nfa_data
                )
            )

            #
            # LR TABLES
            #

            table_data = (

                ParsingTableSerializer
                .serialize_lr(
                    parser
                )
            )

            table_vm = (

                ParsingTableViewModel
                .build_lr(
                    table_data
                )
            )

            data["tables"][
                "action_table"
            ] = (

                table_vm[
                    "action_table"
                ]
            )

            data["tables"][
                "goto_table"
            ] = (

                table_vm[
                    "goto_table"
                ]
            )

            #
            # statistics
            #

            data["statistics"][
                "num_states"
            ] = len(
                parser.dfa.states
            )

        #
        # ======================================================
        # LL1 TABLE
        # ======================================================
        #

        if hasattr(parser, "parsing_table"):

            table_data = (

                ParsingTableSerializer
                .serialize_ll1(
                    parser
                )
            )

            data["tables"][
                "ll1_table"
            ] = (

                ParsingTableViewModel
                .build_ll1(
                    table_data
                )
            )

        #
        # ======================================================
        # FIRST SETS
        # ======================================================
        #

        if hasattr(parser, "first_sets"):

            data["first_sets"] = {

                symbol: sorted(
                    list(values)
                )

                for symbol, values
                in parser.first_sets.items()
            }

        #
        # ======================================================
        # FOLLOW SETS
        # ======================================================
        #

        if hasattr(parser, "follow_sets"):

            data["follow_sets"] = {

                symbol: sorted(
                    list(values)
                )

                for symbol, values
                in parser.follow_sets.items()
            }

        #
        # parsers sin follow
        #

        else:

            data["follow_sets"] = {

                non_terminal: []

                for non_terminal
                in parser.grammar.non_terminals
            }

        #
        # ======================================================
        # conflicts
        # ======================================================
        #

        if hasattr(parser, "conflicts"):

            data["conflicts"] = [

                str(conflict)

                for conflict
                in parser.conflicts
            ]

        return data

    #
    # ==========================================================
    # BUILD PARSE RESULT
    # ==========================================================
    #

    @staticmethod
    def build_parse_result(result):

        return {

            "parse_result": {

                #
                # status
                #

                "accepted":
                    result.accepted,

                "error":
                    result.error,

                #
                # trace
                #

                "trace":

                    TraceSerializer
                    .serialize(
                        result.trace
                    ),

                #
                # syntax tree
                #

                "syntax_tree":

                    SyntaxTreeSerializer
                    .serialize(
                        result.syntax_tree
                    )
            }
        }