#!/usr/bin/env python
"""
A simple example of a few buttons and click handlers.
"""
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.bindings.focus import focus_next, focus_previous
from prompt_toolkit.layout import Layout
from prompt_toolkit.styles import Style

from core.UIModule.ApplicationContainer import *

# Key bindings.
kb = KeyBindings()
kb.add("tab")(focus_next)
kb.add("down")(focus_next)
kb.add("s-tab")(focus_previous)
kb.add("up")(focus_previous)
kb.add("escape")(lambda e: e.app.exit())
kb.add("r")(lambda e: e.app.reset())

# Styling.
style = Style(
    [
        ("left-pane", "bg:#000000 #000000"),
        ("right-pane", "bg:#000000 #ffffff"),
        ("button", "#ffffff"),
        ("button.arrow", "#ffffff"),
        ("button.focused", "bg:#888888"),
        ("text-area.focused", "bg:#ff0000"),
        ("login-frame", "bg:#000000 #ffffff"),
        ("login-textarea", "bg:#444444"),
        ("version-search-box", "bg:#444444")
    ]
)

main_container = ApplicationContainer()
layout = Layout(container=main_container.container, focused_element=main_container.default_focus)
application = Application(layout=layout, key_bindings=kb, style=style, full_screen=True)
main_container.set_app(application)


def main():
    application.run()


if __name__ == "__main__":
    main()
