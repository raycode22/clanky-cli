#!/usr/bin/env python3

import os
import json
import datetime
import questionary
from rich.console import Console
from rich.prompt import Prompt
import requests

# ──────────────────────────────────────────────────────
# CONFIGURATION
# ────────────────────────────────────────────────────
API_KEY = os.getenv("OPENROUTER_API_KEY") or "sk-demo"
MODEL = "deepseek/deepseek-r1-0528:free"
SAVE_DIR = os.path.expanduser("~/Ai/deepseek_save_files")
os.makedirs(SAVE_DIR, exist_ok=True)

API_URL = "https://openrouter.ai/api/v1/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

console = Console()
conversation_history = []

# ────────────────────────────────────────────────────
# DISPLAY HELP AND INTRO
# ────────────────────────────────────────────────────

def show_intro():
    console.clear()
    console.print(r"""
[bold cyan]
╔────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╗
│                                                                                                                                    │
│    ███████╗███████╗██████╗  ██████╗ ██████╗  █████╗     ██╗  ██╗███████╗██╗███████╗███████╗███╗   ██╗██████╗ ██╗   ██╗ ██████╗     │
│    ██╔════╝██╔════╝██╔══██╗██╔═══██╗██╔══██╗██╔══██╗    ██║  ██║██╔════╝██║██╔════╝██╔════╝████╗  ██║██╔══██╗██║   ██║██╔════╝     │
│    █████╗  █████╗  ██║  ██║██║   ██║██████╔╝███████║    ███████║█████╗  ██║███████╗█████╗  ██╔██╗ ██║██████╔╝██║   ██║██║  ███╗    │
│    ██╔══╝  ██╔══╝  ██║  ██║██║   ██║██╔══██╗██╔══██║    ██╔══██║██╔══╝  ██║╚════██║██╔══╝  ██║╚██╗██║██╔══██╗██║   ██║██║   ██║    │
│    ██║     ███████╗██████╔╝╚██████╔╝██║  ██║██║  ██║    ██║  ██║███████╗██║███████║███████╗██║ ╚████║██████╔╝╚██████╔╝╚██████╔╝    │
│    ╚═╝     ╚══════╝╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝    ╚═╝  ╚═╝╚══════╝╚═╝╚══════╝╚══════╝╚═╝  ╚═══╝╚═════╝  ╚═════╝  ╚═════╝     │
│                                                                                                                                    │
╚────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╝
[/bold cyan]
""")
    console.print("[bold]Commands:[/bold] /exit, /reset, /save, /load, /model, /list, /delete, /help\n")

def show_help():
    console.print(
        "[bold yellow]Usage Guide:[/bold yellow]\n"
        "   Type your prompt and press Enter to chat\n"
        "   /reset - Start a new conversation\n"
        "   /save  - Save current chat (JSON + MD)\n"
        "   /load  - Load past conversation\n"
        "   /list  - List saved conversations\n"
        "   /delete - Delete a saved file\n"
        "   Add #TABULATE to format tables\n"
        "   Model: deepseek-r1-0528 (free)\n"
    )

# Chat API Call
def call_api(prompt):
    global conversation_history
    conversation_history.append({"role": "user", "content": prompt})
    payload = {
        "model": MODEL,
        "messages": conversation_history,
        "temperature": 0.7
    }
    try:
        response = requests.post(API_URL, headers=HEADERS, json=payload)
        response.raise_for_status()
        reply = response.json()["choices"][0]["message"]["content"]
        conversation_history.append({"role": "assistant", "content": reply})
        return reply
    except Exception as e:
        return f"[red]Error:[/red] {e}"

# Save and Load

def save_conversation():
    filename = Prompt.ask("  Enter filename (no extension)")
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = os.path.join(SAVE_DIR, f"{filename}_{timestamp}.json")
    md_path = os.path.join(SAVE_DIR, f"{filename}_{timestamp}.md")

    with open(json_path, "w") as f:
        json.dump(conversation_history, f, indent=2)

    with open(md_path, "w") as f:
        for msg in conversation_history:
            f.write(f"### {msg['role'].capitalize()}\n{msg['content']}\n\n")

    console.print(f"[green]Saved:[/green] {json_path} & {md_path}")

def choose_file_interactively():
    files = sorted([f for f in os.listdir(SAVE_DIR) if f.endswith(".json")])
    if not files:
        console.print("[red]No saved conversations found.[/red]")
        return None

    choices = ["  Cancel"] + [f"  {f}" for f in files]
    selected = questionary.select("  Select file to load:", choices=choices).ask()
    if not selected or selected.startswith(""):
        return None

    return os.path.join(SAVE_DIR, selected.split("  ", 1)[-1])

def load_conversation(path):
    global conversation_history
    with open(path, "r") as f:
        conversation_history = json.load(f)
    console.print(f"[green]Loaded from:[/green] {path}")

def list_conversations():
    files = sorted(f for f in os.listdir(SAVE_DIR) if f.endswith(".json"))
    if not files:
        console.print("[red]No saved files.[/red]")
    else:
        console.print("[bold blue]\n  Saved Files:[/bold blue]")
        for f in files:
            console.print(f"    {f}")

def delete_conversation():
    files = sorted([f for f in os.listdir(SAVE_DIR) if f.endswith(".json")])
    if not files:
        console.print("[red]No saved files to delete.[/red]")
        return
    choices = ["  Cancel"] + [f"  {f}" for f in files]
    selected = questionary.select("  Choose file to delete:", choices=choices).ask()
    if not selected or selected.startswith(""):
        return
    path = os.path.join(SAVE_DIR, selected.split("  ", 1)[-1])
    os.remove(path)
    console.print(f"[red]Deleted:[/red] {path}")

# Main Loop

def main():
    show_intro()
    show_help()

    while True:
        user_input = Prompt.ask("[bold green]You[/bold green]")

        if user_input.strip() == "":
            continue
        elif user_input == "/exit":
            console.print("[cyan]Goodbye![/cyan]")
            break
        elif user_input == "/reset":
            conversation_history.clear()
            console.print("[yellow]Conversation reset.[/yellow]")
            continue
        elif user_input == "/save":
            save_conversation()
            continue
        elif user_input == "/load":
            selected_file = choose_file_interactively()
            if selected_file:
                load_conversation(selected_file)
            continue
        elif user_input == "/list":
            list_conversations()
            continue
        elif user_input == "/delete":
            delete_conversation()
            continue
        elif user_input == "/help":
            show_help()
            continue
        elif user_input == "/model":
            console.print("[yellow]Model:[/yellow] deepseek-r1-0528 (free)")
            continue

        response = call_api(user_input)
        if "#TABULATE" in user_input:
            lines = [line.strip() for line in response.splitlines() if line.strip()]
            console.print("[bold yellow]\nTabulated Output:[/bold yellow]\n")
            console.print("\n".join(lines))
        elif "```" in response:
            code = "\n".join([line for line in response.splitlines() if "```" not in line])
            console.print("[bold yellow]Code Output:[/bold yellow]\n")
            console.print(code)
        else:
            console.print(f"[bold yellow]Assistant:[/bold yellow] {response}")

if __name__ == "__main__":
    main()
