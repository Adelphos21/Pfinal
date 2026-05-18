from collections import defaultdict

from app.core.parsing.lr.lr1 import LR1

from app.core.automata.automaton import Automaton
from app.core.automata.state import State
from app.core.automata.transition import Transition


class LALR1(LR1):

    def __init__(self, grammar):

        #
        # mapa:
        #
        # core LR(0) -> estado LALR
        #

        self.core_to_state = {}

        super().__init__(grammar)

    #
    # ==========================================================
    # VALIDACIÓN LALR(1)
    # ==========================================================
    #

    @property
    def is_valid(self):

        return len(self.conflicts) == 0

    #
    # ==========================================================
    # CORE LR(0)
    # ==========================================================
    #

    def core_of_state(self, state):

        """
        El núcleo (core) de un estado LR(1)
        es el conjunto de pares:

            (production.id, dot_position)

        ignorando completamente el lookahead.

        Ejemplo:

            [A -> α • β, $]
            [A -> α • β, )]

        ambos tienen el mismo core:
            (A -> α • β)
        """

        return frozenset(
            (
                item.production.id,
                item.dot_position
            )
            for item in state.items
        )

    #
    # ==========================================================
    # CONSTRUCCIÓN DEL DFA
    # ==========================================================
    #

    def build_dfa(self):

        #
        # Primero construimos el DFA LR(1)
        # canónico normal.
        #

        super().build_dfa()

        #
        # Luego fusionamos estados que tengan
        # el mismo core LR(0).
        #

        self.merge_states()

    #
    # ==========================================================
    # FUSIÓN DE ESTADOS LR(1)
    # ==========================================================
    #

    def merge_states(self):

        #
        # ======================================================
        # AGRUPAR ESTADOS POR CORE
        # ======================================================
        #

        groups = defaultdict(list)

        for state in self.dfa.states.values():

            core = self.core_of_state(
                state
            )

            groups[core].append(
                state
            )

        #
        # ======================================================
        # NUEVO DFA LALR(1)
        # ======================================================
        #

        new_dfa = Automaton()

        #
        # mapa:
        #
        # core -> nuevo estado fusionado
        #

        core_to_new_state = {}

        new_state_id = 0

        #
        # ======================================================
        # CREAR ESTADOS FUSIONADOS
        # ======================================================
        #

        for core, states in groups.items():

            merged_state = State(
                id=new_state_id
            )

            #
            # fusionar todos los items LR(1)
            #
            # IMPORTANTE:
            #
            # NO fusionamos lookaheads en sets.
            #
            # Simplemente conservamos todos
            # los items LR(1).
            #
            # Ejemplo:
            #
            # [A -> α • β, $]
            # [A -> α • β, )]
            #
            # ambos quedan dentro del mismo
            # estado LALR.
            #

            merged_items = set()

            for state in states:

                merged_items.update(
                    state.items
                )

            #
            # agregar items al nuevo estado
            #

            for item in merged_items:

                merged_state.add_item(
                    item
                )

            #
            # registrar estado
            #

            new_dfa.add_state(
                merged_state
            )

            core_to_new_state[
                core
            ] = merged_state

            new_state_id += 1

        #
        # ======================================================
        # ESTADO INICIAL
        # ======================================================
        #

        initial_core = self.core_of_state(
            self.dfa.initial_state
        )

        new_dfa.initial_state = (
            core_to_new_state[
                initial_core
            ]
        )

        #
        # ======================================================
        # RECONSTRUIR TRANSICIONES
        # ======================================================
        #

        #
        # evita duplicados
        #

        added_transitions = set()

        for old_state in self.dfa.states.values():

            #
            # estado origen fusionado
            #

            source_core = self.core_of_state(
                old_state
            )

            source_new_state = (
                core_to_new_state[
                    source_core
                ]
            )

            #
            # transiciones salientes
            #

            transitions = (
                self.dfa.get_transitions_from(
                    old_state
                )
            )

            for transition in transitions:

                #
                # estado destino original
                #

                old_target = self.dfa.get_state(
                    transition.target_id
                )

                #
                # core del destino
                #

                target_core = self.core_of_state(
                    old_target
                )

                #
                # estado destino fusionado
                #

                target_new_state = (
                    core_to_new_state[
                        target_core
                    ]
                )

                #
                # evitar transiciones repetidas
                #

                key = (
                    source_new_state.id,
                    transition.symbol,
                    target_new_state.id
                )

                if key in added_transitions:
                    continue

                added_transitions.add(
                    key
                )

                #
                # crear transición LALR
                #

                new_transition = Transition(
                    source_id=source_new_state.id,
                    symbol=transition.symbol,
                    target_id=target_new_state.id
                )

                new_dfa.add_transition(
                    new_transition
                )

        #
        # reemplazar DFA LR(1)
        # por DFA LALR(1)
        #

        self.dfa = new_dfa

    #
    # ==========================================================
    # REPRESENTACIÓN COMPACTA
    # ==========================================================
    #

    def format_state_items(self, state):

        """
        Convierte:

            [A -> α • β, $]
            [A -> α • β, )]

        en:

            [A -> α • β, $ / )]

        SOLO para visualización.
        """

        grouped = defaultdict(set)

        #
        # agrupar por núcleo LR(0)
        #

        for item in state.items:

            key = (
                item.production,
                item.dot_position
            )

            grouped[key].add(
                item.lookahead
            )

        lines = []

        #
        # construir representación compacta
        #

        for (
            production,
            dot_position
        ), lookaheads in grouped.items():

            right = list(
                production.right
            )

            #
            # insertar punto
            #

            right.insert(
                dot_position,
                "•"
            )

            #
            # juntar lookaheads
            #

            lookahead_text = " / ".join(
                sorted(lookaheads)
            )

            line = (
                f"[{production.left} -> "
                f"{' '.join(right)}, "
                f"{lookahead_text}]"
            )

            lines.append(line)

        return "\n".join(lines)