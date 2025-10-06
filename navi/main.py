#!/usr/bin/env python3
import os
import threading
from openai import OpenAI
from menu import run_cli

client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=os.getenv("HF_API_KEY")
)

command_history = []
current_text = ""
suggestion_timer = None
current_commands = []
loading_callback = None

def get_suggestions(text, update_commands_callback):
    if not text.strip():
        return
    
    if loading_callback:
        loading_callback(True)
    
    try:
        response = client.chat.completions.create(
            model="meta-llama/Llama-3.3-70B-Instruct",
            messages=[
                {"role": "system", "content": "You are a CLI assistant. Return ONLY a JSON array of 3-5 command suggestions as strings, no explanation."},
                {"role": "user", "content": f"Suggest completions for: {text}"}
            ],
            max_tokens=100
        )
        import json
        suggestions = json.loads(response.choices[0].message.content)
        if isinstance(suggestions, list):
            update_commands_callback(suggestions)
    except Exception as e:
        print(f"\nError: {e}")
        if loading_callback:
            loading_callback(False)

def on_text_change(text, update_commands_callback, set_loading):
    global current_text, suggestion_timer, loading_callback
    current_text = text
    loading_callback = set_loading
    
    if loading_callback:
        loading_callback(False)
    
    if suggestion_timer:
        suggestion_timer.cancel()
    
    if text.strip():
        suggestion_timer = threading.Timer(0.5, lambda: get_suggestions(text, update_commands_callback))
        suggestion_timer.start()
    
def log_command(cmd, output):
    command_history.append({"command": cmd, "output": output})

run_cli(current_commands, on_command=log_command, on_text_change=on_text_change)