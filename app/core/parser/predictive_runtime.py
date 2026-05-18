from app.core.parser.parse_result import (
    ParseResult
)

from app.core.parser.parser_errors import (
    LL1UnexpectedTokenError
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

from app.utils.constants import (
    EPSILON,
    ENDMARKER
)


class PredictiveRuntime:

    def __init__(self, parser):

        #
        # parser LL1
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
        # stack predictivo
        #
        # $ start_symbol
        #

        stack = [
            ENDMARKER,
            self.parser.grammar.start_symbol
        ]

        #
        # semantic stack
        #
        # usada para construir
        # syntax tree
        #

        semantic_stack = []

        #
        # nodo raíz
        #

        root = SyntaxTreeNode(
            symbol=self.parser.grammar.start_symbol
        )

        #
        # stack paralelo nodos
        #

        node_stack = [
            root
        ]

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

        while stack:

            #
            # top stack
            #

            top = stack[-1]

            #
            # current token
            #

            current_token = tokens[index]

            #
            # ==================================================
            # ACCEPT
            # ==================================================
            #

            if (
                top == ENDMARKER
                and current_token == ENDMARKER
            ):

                trace.record(
                    parsing_stack=stack,
                    semantic_stack=[
                        node.symbol
                        for node in semantic_stack
                    ],
                    remaining_input=tokens[index:],
                    action="accept"
                )

                stack.pop()

                result.accepted = True

                result.syntax_tree = SyntaxTree(
                    root=root
                )

                return result

            #
            # ==================================================
            # TERMINAL MATCH
            # ==================================================
            #

            if top in self.parser.grammar.terminals:

                #
                # mismatch
                #

                if top != current_token:

                    trace.record(
                        parsing_stack=stack,
                        semantic_stack=[
                            node.symbol
                            for node in semantic_stack
                        ],
                        remaining_input=tokens[index:],
                        action="error"
                    )

                    error = LL1UnexpectedTokenError(
                        top,
                        current_token
                    )

                    result.error = str(error)

                    return result

                #
                # trace
                #

                trace.record(
                    parsing_stack=stack,
                    semantic_stack=[
                        node.symbol
                        for node in semantic_stack
                    ],
                    remaining_input=tokens[index:],
                    action=f"match {current_token}"
                )

                #
                # consumir terminal
                #

                stack.pop()

                terminal_node = node_stack.pop()

                #
                # semantic
                #

                semantic_stack.append(
                    terminal_node
                )

                #
                # avanzar input
                #

                index += 1

                continue

            #
            # ==================================================
            # NON TERMINAL
            # ==================================================
            #

            #
            # M[A, a]
            #

            productions = (
                self.parser.get_table_entry(
                    top,
                    current_token
                )
            )

            #
            # error
            #

            if not productions:

                trace.record(
                    parsing_stack=stack,
                    semantic_stack=[
                        node.symbol
                        for node in semantic_stack
                    ],
                    remaining_input=tokens[index:],
                    action="error"
                )

                error = LL1UnexpectedTokenError(
                    top,
                    current_token
                )

                result.error = str(error)

                return result

            #
            # tomar primera producción
            #

            production = sorted(
                productions,
                key=lambda p: p.id
            )[0]

            #
            # trace ANTES de modificar stack
            #

            trace.record(
                parsing_stack=stack,
                semantic_stack=[
                    node.symbol
                    for node in semantic_stack
                ],
                remaining_input=tokens[index:],
                action=str(production)
            )

            #
            # consumir no terminal
            #

            stack.pop()

            current_node = node_stack.pop()

            #
            # epsilon production
            #

            if production.right == (EPSILON,):

                epsilon_node = SyntaxTreeNode(
                    symbol=EPSILON
                )

                current_node.children.append(
                    epsilon_node
                )

                semantic_stack.append(
                    current_node
                )

                continue

            #
            # crear hijos
            #

            children = []

            for symbol in production.right:

                child = SyntaxTreeNode(
                    symbol=symbol
                )

                children.append(
                    child
                )

            #
            # conectar hijos
            #

            current_node.children.extend(
                children
            )

            #
            # push reverse
            #

            for child in reversed(children):

                stack.append(
                    child.symbol
                )

                node_stack.append(
                    child
                )

            #
            # semantic
            #

            semantic_stack.append(
                current_node
            )

        #
        # fallo inesperado
        #

        trace.record(
            parsing_stack=stack,
            semantic_stack=[
                node.symbol
                for node in semantic_stack
            ],
            remaining_input=tokens[index:],
            action="error"
        )

        result.error = (
            "Unexpected end of parsing"
        )

        return result