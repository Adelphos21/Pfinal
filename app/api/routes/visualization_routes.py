from fastapi import APIRouter

from app.core.grammar.grammar import (
    Grammar
)

from app.core.parser.parser_factory import (
    ParserFactory
)

from app.services.visualization_service import (
    VisualizationService
)

router = APIRouter(
    prefix="/visualization",
    tags=["Visualization"]
)


#
# ==========================================================
# BUILD PARSER
# ==========================================================
#

@router.post("/build")

def build_parser(payload: dict):

    grammar_text = payload["grammar"]

    parser_type = payload["parser"]

    grammar = Grammar.from_string(
        grammar_text
    )

    parser = ParserFactory.create(
        parser_type,
        grammar
    )

    return (
        VisualizationService
        .build_parser_visualization(
            parser
        )
    )


#
# ==========================================================
# PARSE INPUT
# ==========================================================
#

@router.post("/parse")

def parse_input(payload: dict):

    grammar_text = payload["grammar"]

    parser_type = payload["parser"]

    tokens = payload["tokens"]

    grammar = Grammar.from_string(
        grammar_text
    )

    parser = ParserFactory.create(
        parser_type,
        grammar
    )

    result = parser.parse(
        tokens
    )

    parser_data = (
        VisualizationService
        .build_parser_visualization(
            parser
        )
    )

    parse_data = (
        VisualizationService
        .build_parse_result(
            result
        )
    )

    return {

        **parser_data,

        **parse_data
    }