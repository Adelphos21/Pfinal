from collections import defaultdict

from app.utils.constants import (
    EPSILON,
    ENDMARKER
)


def compute_first(grammar):

    first = defaultdict(set)

    for terminal in grammar.terminals:
        first[terminal].add(terminal)

    #
    # endmarker $
    #
    first[ENDMARKER].add(ENDMARKER)

    for non_terminal in grammar.non_terminals:
        first[non_terminal] = set()

    changed = True

    while changed:

        changed = False

        for production in grammar.productions:

            left = production.left
            right = production.right

            if not right:

                if EPSILON not in first[left]:

                    first[left].add(EPSILON)

                    changed = True

                continue

            for symbol in right:

                before = len(first[left])

                first[left].update(
                    first[symbol] - {EPSILON}
                )

                after = len(first[left])

                if after > before:
                    changed = True

                if EPSILON not in first[symbol]:
                    break

            else:

                if EPSILON not in first[left]:

                    first[left].add(EPSILON)

                    changed = True

    return dict(first)


def first_of_sequence(
    sequence,
    first_sets
):

    result = set()

    if not sequence:

        result.add(EPSILON)

        return result

    for symbol in sequence:

        if symbol == EPSILON:

            result.add(EPSILON)

            continue

        result.update(
            first_sets[symbol] - {EPSILON}
        )

        if EPSILON not in first_sets[symbol]:
            break

    else:
        result.add(EPSILON)

    return result


def compute_follow(
    grammar,
    first_sets
):

    follow = defaultdict(set)

    follow[grammar.start_symbol].add(
        ENDMARKER
    )

    for non_terminal in grammar.non_terminals:
        follow[non_terminal] = set(
            follow[non_terminal]
        )

    changed = True

    while changed:

        changed = False

        for production in grammar.productions:

            left = production.left
            right = production.right

            for i, symbol in enumerate(right):

                if symbol not in grammar.non_terminals:
                    continue

                beta = right[i + 1:]

                first_beta = first_of_sequence(
                    beta,
                    first_sets
                )

                before = len(follow[symbol])

                follow[symbol].update(
                    first_beta - {EPSILON}
                )

                if (
                    not beta
                    or EPSILON in first_beta
                ):

                    follow[symbol].update(
                        follow[left]
                    )

                after = len(follow[symbol])

                if after > before:
                    changed = True

    return dict(follow)