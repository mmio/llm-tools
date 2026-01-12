from collections.abc import Sequence
from typing import TypeVar

from prompt_toolkit import Application
from prompt_toolkit.application import get_app
from prompt_toolkit.formatted_text import AnyFormattedText
from prompt_toolkit.layout import HSplit
from prompt_toolkit.shortcuts.dialogs import _return_none, _create_app
from prompt_toolkit.styles import BaseStyle
from prompt_toolkit.widgets import RadioList, Dialog, Label, Button

_T = TypeVar("_T")

def radiolist_dialog(
    title: AnyFormattedText = "",
    text: AnyFormattedText = "",
    ok_text: str = "Ok",
    cancel_text: str = "Cancel",
    values: Sequence[tuple[_T, AnyFormattedText]] | None = None,
    default: _T | None = None,
    style: BaseStyle | None = None,
) -> Application[_T]:
    """
    Display a simple list of element the user can choose amongst.

    Only one element can be selected at a time using Arrow keys and Enter.
    The focus can be moved between the list and the Ok/Cancel button with tab.
    """
    if values is None:
        values = []

    def ok_handler() -> None:
        get_app().exit(result=radio_list.current_value)

    radio_list = RadioList(
        values=values,
        default=default,
        select_on_focus=True,
        open_character='',
        close_character='',

    )

    dialog = Dialog(
        title=title,
        body=HSplit(
            [Label(text=text, dont_extend_height=True), radio_list],
            padding=1,
        ),
        buttons=[
            Button(text=ok_text, handler=ok_handler, left_symbol='[', right_symbol=']'),
            Button(text=cancel_text, handler=_return_none, left_symbol='[', right_symbol=']'),
        ],
        with_background=True,
    )

    return _create_app(dialog, style)
