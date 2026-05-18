class TraceSerializer:

    @staticmethod
    def serialize(trace):

        if trace is None:

            return []

        return [

            {
                #
                # raw stack
                #

                "stack":
                    frame.parsing_stack,

                #
                # display stack
                #

                "stack_display":

                    " ".join(
                        map(
                            str,
                            frame.parsing_stack
                        )
                    ),

                #
                # raw input
                #

                "input":
                    frame.remaining_input,

                #
                # display input
                #

                "input_display":

                    " ".join(
                        frame.remaining_input
                    ),

                #
                # action
                #

                "action":
                    frame.action
            }

            for frame
            in trace.frames
        ]