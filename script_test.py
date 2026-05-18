from app.core.grammar.grammar import (
    Grammar
)

from app.core.parser.parser_factory import (
    ParserFactory
)


#
# ==========================================================
# HELPER
# ==========================================================
#

def run_slr1_test(
    title,
    grammar_text,
    tokens
):

    print()
    print("=" * 60)
    print(title)
    print("=" * 60)
    print()

    #
    # ======================================================
    # GRAMMAR
    # ======================================================
    #

    grammar = Grammar.from_string(
        grammar_text
    )

    #
    # ======================================================
    # PRINT GRAMMAR
    # ======================================================
    #

    print("========== GRAMMAR ==========")

    for production in grammar.productions:

        print(production)

    print()

    #
    # ======================================================
    # BUILD PARSER
    # ======================================================
    #

    parser = ParserFactory.create(
        parser_type="slr1",
        grammar=grammar
    )

    #
    # ======================================================
    # VALIDATION
    # ======================================================
    #

    print("========== IS VALID SLR1 ==========")

    print(
        parser.is_valid
    )

    print()

    #
    # ======================================================
    # FIRST SETS
    # ======================================================
    #

    print("========== FIRST SETS ==========")

    for symbol in sorted(
        parser.first_sets
    ):

        print(
            f"FIRST({symbol}) = "
            f"{parser.first_sets[symbol]}"
        )

    print()

    #
    # ======================================================
    # FOLLOW SETS
    # ======================================================
    #

    print("========== FOLLOW SETS ==========")

    for symbol in sorted(
        parser.follow_sets
    ):

        print(
            f"FOLLOW({symbol}) = "
            f"{parser.follow_sets[symbol]}"
        )

    print()

    #
    # ======================================================
    # DFA STATES
    # ======================================================
    #

    print("========== DFA STATES ==========")

    for state in sorted(
        parser.dfa.states.values(),
        key=lambda s: s.id
    ):

        print(state)

        print()

    #
    # ======================================================
    # DFA TRANSITIONS
    # ======================================================
    #

    print("========== DFA TRANSITIONS ==========")

    for transition in sorted(
        parser.dfa.transitions,
        key=lambda t: (
            t.source_id,
            t.symbol,
            t.target_id
        )
    ):

        print(transition)

    print()

    #
    # ======================================================
    # ACTION TABLE
    # ======================================================
    #

    print("========== ACTION TABLE ==========")

    for key in sorted(
        parser.action_table
    ):

        state, symbol = key

        actions = parser.action_table[key]

        print(
            f"ACTION[{state}, {symbol}] = "
            f"{actions}"
        )

    print()

    #
    # ======================================================
    # GOTO TABLE
    # ======================================================
    #

    print("========== GOTO TABLE ==========")

    for key in sorted(
        parser.goto_table
    ):

        state, symbol = key

        target = parser.goto_table[key]

        print(
            f"GOTO[{state}, {symbol}] = "
            f"{target}"
        )

    print()

    #
    # ======================================================
    # CONFLICTS
    # ======================================================
    #

    print("========== CONFLICTS ==========")

    if parser.conflicts:

        for conflict in parser.conflicts:

            print(conflict)

    else:

        print("No conflicts")

    print()

    #
    # ======================================================
    # TOKENS
    # ======================================================
    #

    print("========== TOKENS ==========")

    print(tokens)

    print()

    #
    # ======================================================
    # PARSE
    # ======================================================
    #

    result = parser.parse(
        tokens
    )

    #
    # ======================================================
    # ACCEPTED
    # ======================================================
    #

    print("========== ACCEPTED ==========")

    print(
        result.accepted
    )

    print()

    #
    # ======================================================
    # TRACE
    # ======================================================
    #

    print("========== TRACE FRAMES ==========")

    if result.trace:

        for i, frame in enumerate(
            result.trace.frames,
            start=1
        ):

            print(f"FRAME {i}")

            print(frame)

            print()

    #
    # ======================================================
    # SYNTAX TREE
    # ======================================================
    #

    print("========== SYNTAX TREE ==========")

    if result.syntax_tree:

        print(
            result.syntax_tree
        )

    print()


#
# ==========================================================
# TEST
# ==========================================================
#

grammar_text = """
S -> id | V := E
V -> id
E -> V | n
"""

tokens = [
    "id",
    ":=",
    "n"
]

run_slr1_test(
    title="SLR1 TEST",
    grammar_text=grammar_text,
    tokens=tokens
)