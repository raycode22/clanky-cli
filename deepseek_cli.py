#!/usr/bin/env python3

import os
import json
import datetime
import threading
import time
import textwrap
import questionary
import requests
from rich.console import Console
from rich.prompt import Prompt
from rich.live import Live
from rich.text import Text

# ──────────────────────────────────────────────────────
# CONSTANTS & CONFIGURATION
# ──────────────────────────────────────────────────────
API_KEY = os.getenv("OPENROUTER_API_KEY") or "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"
MODEL = "deepseek/deepseek-r1-0528:free"
SAVE_DIR = os.path.expanduser("~/Ai/deepseek_save_files")
os.makedirs(SAVE_DIR, exist_ok=True)
MAX_WIDTH = 80  # Maximum line width for output

API_URL = "https://openrouter.ai/api/v1/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# ANSI color codes
CYAN = "\033[36m"
ORANGE = "\033[38;5;208m"
RESET = "\033[0m"

# ──────────────────────────────────────────────────────
# APPLICATION CLASS
# ──────────────────────────────────────────────────────
class ClankyChat:
    def __init__(self):
        self.console = Console()
        self.conversation_history = []
        self.show_banner()
        self.show_help()
        self.cancelled = False
        self.active_request = None

    # ──────────────────────────────────────────────────────
    # UI ELEMENTS
    # ──────────────────────────────────────────────────────
    def show_banner(self):
        ascii_art = [
            "╔───────────────────────────────────────────────────────────────────────────────────╗",
            "│                                                                                   │",
            "│     ██████╗██╗      █████╗ ███╗   ██╗██╗  ██╗██╗   ██╗      ██████╗██╗     ██╗    │",
            "│    ██╔════╝██║     ██╔══██╗████╗  ██║██║ ██╔╝╚██╗ ██╔╝     ██╔════╝██║     ██║    │",
            "│    ██║     ██║     ███████║██╔██╗ ██║█████╔╝  ╚████╔╝█████╗██║     ██║     ██║    │",
            "│    ██║     ██║     ██╔══██║██║╚██╗██║██╔═██╗   ╚██╔╝ ╚════╝██║     ██║     ██║    │",
            "│    ╚██████╗███████╗██║  ██║██║ ╚████║██║  ██╗   ██║        ╚██████╗███████╗██║    │",
            "│     ╚═════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝   ╚═╝         ╚═════╝╚══════╝╚═╝    │",
            "│                                                                                   │",
            "╚───────────────────────────────────────────────────────────────────────────────────╝"
        ]

        split_index = len(ascii_art) // 2
        for i, line in enumerate(ascii_art):
            color = CYAN if i < split_index else ORANGE
            print(f"{color}{line}{RESET}")

    def show_help(self):
        self.console.print(
            "[bold]Commands:[/bold] /exit, /reset, /save, /load, /model, /list, /delete, /help\n"
            "[bold yellow]Usage Guide:[/bold yellow]\n"
            "   Type your prompt and press Enter to chat\n"
            "   /reset - Start a new conversation\n"
            "   /save  - Save current chat (JSON + MD)\n"
            "   /load  - Load past conversation\n"
            "   /list  - List saved conversations\n"
            "   /delete - Delete a saved file\n"
            "   Add #TABULATE to format tables\n"
            "   Press [bold]Ctrl+C[/bold] during thinking to cancel request\n"
        )

    # ──────────────────────────────────────────────────────
    # TEXT FORMATTING
    # ──────────────────────────────────────────────────────
    def format_output(self, text):
        """Format text output with wrapping and indentation preservation"""
        # Preserve code blocks and tables
        if "```" in text or "|" in text or "#TABULATE" in text:
            return text

        # Format regular text with wrapping
        formatted_lines = []
        for line in text.split('\n'):
            if line.strip() == '':  # Preserve empty lines
                formatted_lines.append('')
            else:
                # Preserve existing indentation
                leading_spaces = len(line) - len(line.lstrip())
                indent = ' ' * leading_spaces

                # Wrap the content while preserving indentation
                wrapped = textwrap.fill(
                    line.strip(),
                    width=MAX_WIDTH - leading_spaces,
                    initial_indent=indent,
                    subsequent_indent=indent,
                    break_long_words=False,
                    break_on_hyphens=False
                )
                formatted_lines.append(wrapped)
        return '\n'.join(formatted_lines)

    # ──────────────────────────────────────────────────────
    # API COMMUNICATION
    # ──────────────────────────────────────────────────────
    def call_api(self, prompt):
        try:
            self.conversation_history.append({"role": "user", "content": prompt})
            payload = {
                "model": MODEL,
                "messages": self.conversation_history,
                "temperature": 0.7
            }
            self.active_request = requests.post(
                API_URL,
                headers=HEADERS,
                json=payload,
                timeout=300,
                stream=True
            )
            self.active_request.raise_for_status()
            reply = self.active_request.json()["choices"][0]["message"]["content"]
            self.conversation_history.append({"role": "assistant", "content": reply})
            return reply
        except Exception as e:
            return f"[red]Error:[/red] {e}"
        finally:
            self.active_request = None

    def run_with_spinner(self, func, *args, **kwargs):
        done = threading.Event()
        result = [None]
        self.cancelled = False

        def wrapper():
            try:
                result[0] = func(*args, **kwargs)
            finally:
                done.set()

        thread = threading.Thread(target=wrapper, daemon=True)
        thread.start()

        dots = ["", ".", "..", "..."]
        i = 0

        try:
            with Live(console=self.console) as live:
                while not done.is_set():
                    # Update spinner
                    live.update(Text(f"Thinking{dots[i % len(dots)]}", style="bold cyan"))
                    i += 1

                    # Check if cancellation is needed
                    if self.cancelled:
                        if self.active_request:
                            self.active_request.close()
                        done.set()
                        return None

                    time.sleep(0.5)
        except KeyboardInterrupt:
            self.cancelled = True
            self.console.print("\n[red]Request cancelled by user.[/red]")
            if self.conversation_history and self.conversation_history[-1]["role"] == "user":
                self.conversation_history.pop()
            return None

        return result[0]

    # ──────────────────────────────────────────────────────
    # FILE OPERATIONS
    # ──────────────────────────────────────────────────────
    def save_conversation(self):
        filename = Prompt.ask("  Enter filename (no extension)")
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        base_path = os.path.join(SAVE_DIR, f"{filename}_{timestamp}")

        # Save JSON
        json_path = f"{base_path}.json"
        with open(json_path, "w") as f:
            json.dump(self.conversation_history, f, indent=2)

        # Save Markdown
        md_path = f"{base_path}.md"
        with open(md_path, "w") as f:
            for msg in self.conversation_history:
                formatted_content = self.format_output(msg['content'])
                f.write(f"### {msg['role'].capitalize()}\n{formatted_content}\n\n")

        self.console.print(f"[green]Saved:[/green] {json_path} & {md_path}")

    def choose_file(self, action="load"):
        files = sorted(f for f in os.listdir(SAVE_DIR) if f.endswith(".json"))
        if not files:
            self.console.print("[red]No saved conversations found.[/red]")
            return None

        action_symbol = "" if action == "load" else ""
        choices = ["  Cancel"] + [f"{action_symbol}  {f}" for f in files]
        selected = questionary.select(f"{action_symbol}  Select file to {action}:", choices=choices).ask()

        if not selected or selected.startswith(""):
            return None
        return os.path.join(SAVE_DIR, selected.split("  ", 1)[-1])

    def load_conversation(self):
        selected_file = self.choose_file("load")
        if selected_file:
            with open(selected_file, "r") as f:
                self.conversation_history = json.load(f)
            self.console.print(f"[green]Loaded from:[/green] {selected_file}")

    def list_conversations(self):
        files = sorted(f for f in os.listdir(SAVE_DIR) if f.endswith(".json"))
        if not files:
            self.console.print("[red]No saved files.[/red]")
            return

        self.console.print("[bold blue]\n  Saved Files:[/bold blue]")
        for f in files:
            self.console.print(f"    {f}")

    def delete_conversation(self):
        selected_file = self.choose_file("delete")
        if selected_file:
            os.remove(selected_file)
            self.console.print(f"[red]Deleted:[/red] {selected_file}")

    # ──────────────────────────────────────────────────────
    # MAIN LOOP
    # ──────────────────────────────────────────────────────
    def run(self):
        while True:
            try:
                user_input = Prompt.ask("[bold green]Ask anything[/bold green]")

                if not user_input.strip():
                    continue

                # Handle commands
                command = user_input.strip().lower()
                if command == "/exit":
                    self.console.print("[cyan]Goodbye![/cyan]")
                    return
                elif command == "/reset":
                    self.conversation_history = []
                    self.console.print("[yellow]Conversation reset.[/yellow]")
                    continue
                elif command == "/save":
                    self.save_conversation()
                    continue
                elif command == "/load":
                    self.load_conversation()
                    continue
                elif command == "/list":
                    self.list_conversations()
                    continue
                elif command == "/delete":
                    self.delete_conversation()
                    continue
                elif command == "/help":
                    self.show_help()
                    continue
                elif command == "/model":
                    self.console.print(f"[yellow]Model:[/yellow] {MODEL}")
                    continue

                # Process user input
                response = self.run_with_spinner(self.call_api, user_input)

                # Handle response
                if response is None:
                    continue  # Cancelled request

                # Format and display response
                if "#TABULATE" in user_input:
                    if response:
                        lines = [line.strip() for line in response.splitlines() if line.strip()]
                        self.console.print("[bold yellow]\nTabulated Output:[/bold yellow]\n")
                        self.console.print("\n".join(lines))
                else:
                    if response:
                        formatted_response = self.format_output(response)
                        # Create a bordered panel for better readability
                        self.console.print("\n" + "-" * MAX_WIDTH)
                        self.console.print(f"[bold yellow]Assistant:[/bold yellow]")
                        self.console.print(formatted_response)
                        self.console.print("-" * MAX_WIDTH + "\n")
                    else:
                        self.console.print("[bold red]Error: No response received[/bold red]")

            except KeyboardInterrupt:
                self.console.print("\n[cyan]Goodbye![/cyan]")
                return
            except Exception as e:
                self.console.print(f"[bold red]Error:[/bold red] {str(e)}")

# ──────────────────────────────────────────────────────
# MAIN EXECUTION
# ──────────────────────────────────────────────────────
if __name__ == "__main__":
    chat_app = ClankyChat()
    chat_app.run()
