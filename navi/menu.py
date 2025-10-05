#!/usr/bin/env python3
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
import subprocess

commands = ["sudo apt update", "sudo apt", "docker ps -a", "git status", "exit"]
completer = WordCompleter(commands, ignore_case=True, sentence=True)
session = PromptSession(completer=completer)

while True:
    try:
        user_input = session.prompt("CLI> ")
        if user_input.lower() == "exit":
            break
        user_input = user_input.split(" ")

        result = subprocess.run(
            user_input,
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)
    except KeyboardInterrupt:
        continue
    except EOFError:
        break

