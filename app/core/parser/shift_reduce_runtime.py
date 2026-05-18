from app.core.parser.parse_result import (
    ParseResult
)

from app.core.parser.parser_errors import (
    LRUnexpectedTokenError
)

from app.core.tracing.trace_recorder import (
    TraceRecorder
)

from app.core.trees.syntax_tree_node import (
    SyntaxTreeNode
)

from app.core.trees.syntax_tree import (
    SyntaxTree
)

from app.utils.constants import ENDMARKER


class ShiftReduceRuntime:

    def __init__(self, parser):

        #
        # parser LR
        #
        # LR0
        # SLR1
        # LR1
        # LALR1
        #

        self.parser = parser

    #
    # ==================================================
    # PARSE
    # ==================================================
    #

    def parse(self, tokens: list[str]):

        #
        # agregar $
        #

        tokens = list(tokens) + [ENDMARKER]

        #
        # pila:
        #
        # 0 symbol state symbol state ...
        #

        stack = [0]

        #
        # semantic stack
        #
        # usada para construir
        # árbol derivación
        #

        semantic_stack = []

        #
        # índice entrada
        #

        index = 0

        #
        # tracing
        #

        trace = TraceRecorder()

        #
        # resultado
        #

        result = ParseResult(
            accepted=False,
            trace=trace
        )

        #
        # loop principal
        #

        while True:

            #
            # estado actual
            #

            state = stack[-1]

            #
            # token actual
            #

            current_token = tokens[index]

            #
            # ACTION[state, token]
            #

            key = (
                state,
                current_token
            )

            actions = self.parser.action_table.get(
                key,
                set()
            )

            #
            # error sintáctico
            #

            if not actions:

                trace.record(
                    parsing_stack=stack,
                    semantic_stack=[
                        node.symbol
                        for node in semantic_stack
                    ],
                    remaining_input=tokens[index:],
                    action="error"
                )

                error = LRUnexpectedTokenError(
                    state,
                    current_token
                )

                result.error = str(error)

                return result

            #
            # tomar primera acción
            #

            action = sorted(actions)[0]

            #trace
            trace.record(
                parsing_stack=stack,
                semantic_stack=[
                    node.symbol
                    for node in semantic_stack
                ],
                remaining_input=tokens[index:],
                action=action
            )

           

            #
            # ==================================================
            # SHIFT
            # ==================================================
            #

            if self.parser.is_shift_action(
                action
            ):

                target = self.parser.get_shift_target(
                    action
                )

                #
                # push terminal
                #

                stack.append(
                    current_token
                )

                #
                # push estado
                #

                stack.append(
                    target
                )

                #
                # crear hoja terminal
                #

                terminal_node = SyntaxTreeNode(
                    symbol=current_token
                )

                semantic_stack.append(
                    terminal_node
                )

                #
                # consumir token
                #

                index += 1

                continue

            #
            # ==================================================
            # REDUCE
            # ==================================================
            #

            if self.parser.is_reduce_action(
                action
            ):

                production_id = (
                    self.parser.get_reduce_production_id(
                        action
                    )
                )

                production = (
                    self.parser.grammar
                    .get_production_by_id(
                        production_id
                    )
                )

                #
                # ==========================================
                # construir hijos
                # ==========================================
                #

                children = []

                for _ in range(len(production.right)):

                    child = semantic_stack.pop()

                    children.append(child)

                #
                # restaurar orden
                #

                children.reverse()

                #
                # crear nodo padre
                #

                parent = SyntaxTreeNode(
                    symbol=production.left,
                    children=children
                )

                #
                # push semantic node
                #

                semantic_stack.append(
                    parent
                )

                #
                # longitud RHS
                #

                rhs_size = len(
                    production.right
                )

                #
                # pop parsing stack
                #

                pop_count = rhs_size * 2

                for _ in range(pop_count):

                    stack.pop()

                #
                # estado después pop
                #

                state_after_pop = stack[-1]

                #
                # GOTO
                #

                goto_key = (
                    state_after_pop,
                    production.left
                )

                goto_state = (
                    self.parser.goto_table[
                        goto_key
                    ]
                )

                #
                # push non-terminal
                #

                stack.append(
                    production.left
                )

                #
                # push goto state
                #

                stack.append(
                    goto_state
                )

                continue

            #
            # ==================================================
            # ACCEPT
            # ==================================================
            #

            if self.parser.is_accept_action(
                action
            ):

                result.accepted = True

                #
                # árbol final
                #

                if semantic_stack:

                    result.syntax_tree = (
                        SyntaxTree(
                            root=semantic_stack[-1]
                        )
                    )

                return result

    #
    # ==================================================
    # HELPERS
    # ==================================================
    #

    def format_stack(self, stack):

        return "$ " + " ".join(
            str(x)
            for x in stack
        )