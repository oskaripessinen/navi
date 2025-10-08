#!/usr/bin/env python3
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.application import get_app
from prompt_toolkit.formatted_text import HTML
import os


def run_cli(commands, *, on_command=None, on_text_change=None):
    completer = WordCompleter(commands, ignore_case=True, sentence=True)
    loading = {"status": False}
    out_path = os.getenv("NAVI_OUT")
    
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

        try:
            app = get_app()
            app.invalidate()
        except:
            pass
    
    def update_commands(new_commands):
        try:
            nonlocal completer
            loading["status"] = False
            completer = WordCompleter(new_commands, ignore_case=True, sentence=True)
            session.completer = completer
            app = get_app()
            if app.current_buffer:
                app.current_buffer.start_completion()
        except:
            pass

    def buffer_changed(buffer):
        if on_text_change:
            on_text_change(buffer.text, update_commands, set_loading)
    if on_text_change:
        session.default_buffer.on_text_changed += buffer_changed

    while True:
        try:
            user_input = session.prompt("navi> ")
            if user_input.lower() == "exit":
                return
            if on_command:
                on_command(user_input, "")
            if out_path:
                try:
                    with open(out_path, "w", encoding="utf-8") as f:
                        f.write(user_input.strip() + "\n")
                except:
                    pass
            return
        except (KeyboardInterrupt, EOFError):
            return



