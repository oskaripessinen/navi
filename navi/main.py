#!/usr/bin/env python3
import os
import sys
import json
import threading
import warnings
import argparse
from openai import OpenAI
from menu import run_cli
from InquirerPy import inquirer
from InquirerPy.base.control import Choice

warnings.filterwarnings("ignore", category=RuntimeWarning)

client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=os.getenv("HF_API_KEY"),
)

command_history = []
current_text = ""
suggestion_timer = None
loading_callback = None


def ask_ai(question: str) -> str:
    try:
        resp = client.chat.completions.create(
            model="meta-llama/Llama-3.3-70B-Instruct",
            messages=[
                {'role': 'system', 'content': 'You are a helpful CLI/Dev assistant. Return ONLY a JSON array of 1-5 command suggestions as strings and their short explanation in array format.'},
                {"role": "user", "content": question},
            ],
            max_tokens=400,
            temperature=0.2,
        )
        commands = resp.choices[0].message.content
        commands = commands.replace('\\', '\\\\')
        commands = f"[{commands.strip()}]"

        commands = json.loads(commands)


        command_dict = {cmd: desc for cmd, desc in commands}

        choices = inquirer.select(
            message="command --- description",
            choices=list(command_dict.keys()),  
            transformer=lambda result: f"{result} - {command_dict[result]}" 
        ).execute()
        return choices
    except Exception as e:
        return f"Error: {e}"


def get_suggestions(text, update_commands_callback):
    if not text.strip():
        return
    if loading_callback:
        loading_callback(True)
    try:
        resp = client.chat.completions.create(
            model="meta-llama/Llama-3.3-70B-Instruct",
            messages=[
                {"role": "system", "content": "You are a CLI assistant. Return ONLY a JSON array of 3-5 command suggestions as strings, no explanation."},
                {"role": "user", "content": f"Suggest completions for: {text}"},
            ],
            max_tokens=100,
            temperature=0.2,
        )
        suggestions = json.loads(resp.choices[0].message.content)
        if isinstance(suggestions, list):
            update_commands_callback(suggestions)
    except Exception as e:
        print(f"\nError: {e}")
        if loading_callback:
            loading_callback(False)


def on_text_change(text, update_commands_callback, set_loading):
    global suggestion_timer, loading_callback
    loading_callback = set_loading
    if loading_callback:
        loading_callback(False)
    if suggestion_timer:
        suggestion_timer.cancel()
    if text.strip():
        suggestion_timer = threading.Timer(0.3, lambda: get_suggestions(text, update_commands_callback))
        suggestion_timer.start()


def log_command(cmd, output):
    command_history.append({"command": cmd, "output": output})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="navi",
        description="Interactive command navigator and AI helper.",
        epilog=(
            "Usage:\n"
            "  navi                 Start interactive mode\n"
            "  navi \"question\"     Ask AI directly (same as --ask)\n"
            "  navi --ask \"question\"\n"
            "  navi -h | --help     Show this help\n"
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("--ask", nargs="+", help="Ask AI directly (same as passing a positional question).")
    parser.add_argument("question", nargs="*", help="Positional question to ask AI directly.")
    args = parser.parse_args()

    if args.ask or args.question:
        q = " ".join(args.ask or args.question).strip()
        if not q:
            print("Give a question, e.g. navi \"how to list docker containers?\"")
            sys.exit(1)
        selected = ask_ai(q)
        out_path = os.getenv("NAVI_OUT")
        if out_path and selected and not selected.startswith("Error:"):
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(selected.strip() + "\n")
        else:
            print(selected)
        sys.exit(0)

    run_cli(
        commands=[],
        on_command=log_command,
        on_text_change=on_text_change,
    )