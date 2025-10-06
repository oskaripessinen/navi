#!/usr/bin/env python3
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.application import get_app
from prompt_toolkit.formatted_text import HTML
import sys


def run_cli(commands, *, on_command=None, on_text_change=None):
    completer = WordCompleter(commands, ignore_case=True, sentence=True)
    loading = {"status": False}
    
    def bottom_toolbar():
        if loading["status"]:
            return HTML('<b>Loading...</b>')
        return ""
    
    session = PromptSession(
        completer=completer,
        bottom_toolbar=bottom_toolbar
    )
    
    def set_loading(status):
        loading["status"] = status
    
    def update_commands(new_commands):
        nonlocal completer
        loading["status"] = False
        completer = WordCompleter(new_commands, ignore_case=True, sentence=True)
        session.completer = completer
        app = get_app()
        if app.current_buffer:
            app.current_buffer.start_completion()

    def buffer_changed(buffer):
        if on_text_change:
            on_text_change(buffer.text, update_commands, set_loading)

    while True:
        try:
            if on_text_change:
                session.default_buffer.on_text_changed += buffer_changed
            
            user_input = session.prompt("navi> ")
            
            if user_input.lower() == "exit":
                break
            
            sys.stdout.flush()
            return user_input

        except KeyboardInterrupt:
            continue
        except EOFError:
            break



