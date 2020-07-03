from __future__ import annotations

import operator
from typing import Callable, Dict, Generator, List, Tuple, Union

import tinycss2
from typing_extensions import Literal

from gaphor.core.styling.declarations import StyleDeclarations, parse_declarations
from gaphor.core.styling.parser import SelectorError
from gaphor.core.styling.selectors import compile_selector_list

MATCH_SORT_KEY = operator.itemgetter(0, 1)


def merge_styles(styles) -> Dict[str, object]:
    style = {}
    for s in styles:
        style.update(s)
    return style


class CompiledStyleSheet:
    def __init__(self, css):
        self.selectors = [
            (selspec[0], selspec[1], order, declarations)
            for order, (selspec, declarations) in enumerate(parse_style_sheet(css))
            if selspec != "error"
        ]

    def match(self, element) -> Dict[str, object]:
        results = sorted(
            (
                (specificity, order, declarations)
                for pred, specificity, order, declarations in self.selectors
                if pred(element)
            ),
            key=MATCH_SORT_KEY,
        )
        return merge_styles(decl for _, _, decl in results)


def parse_style_sheet(
    css,
) -> Generator[
    Union[
        Tuple[Tuple[Callable[[object], bool], Tuple[int, int, int]], Dict[str, object]],
        Tuple[Literal["error"], Union[tinycss2.ast.ParseError, SelectorError]],
    ],
    None,
    None,
]:
    rules = tinycss2.parse_stylesheet(
        css or "", skip_comments=True, skip_whitespace=True
    )
    for rule in rules:
        if rule.type == "error":
            assert isinstance(rule, tinycss2.ast.ParseError)
            yield ("error", rule)  # type: ignore[misc]
            continue
        try:
            selectors = compile_selector_list(rule.prelude)
        except SelectorError as e:
            yield ("error", e)  # type: ignore[misc]
            continue

        declaration = {
            prop: value
            for prop, value in (
                (prop, StyleDeclarations(prop, value))
                for prop, value in parse_declarations(rule)
            )
            if value is not None
        }

        yield from ((selector, declaration) for selector in selectors)