# Clanky CLI - Terminal-Based AI Assistant

A terminal-native intelligent assistant powered by any OpenRouter-compatible LLM. Built with flexibility in mind, Clanky gives users the freedom to choose their own model.

> **Clanky AI – for the Clankers, by the Clankers.**

---

## ✅ Features

* 💬 Supports any OpenRouter-compatible model
* 💾 Save/load chat history as `.json` and `.md`
* 📂 Default save location: `~/your/file/path`
* 📚 Markdown-formatted saved sessions
* ⌨️ Arrow-key navigation for loading sessions
* 🚫 Auto-save removed by user preference
* ⬅️ Option to cancel loading and return to main chat
* 🖼 Terminal-style icons (lsd-like) using Nerd Fonts
* 🧠 Tabulated and code-formatted responses

---

## 📦 Requirements

* Python 3.8+
* Packages:

  ```bash
  pip install rich questionary requests
  ```
* Terminal with [Nerd Font](https://www.nerdfonts.com/) support for proper icon display

---

## 🚀 How to Run

1. **Clone the project:**

   ```bash
   git clone https://github.com/yourusername/clanky-cli.git
   cd clanky-cli
   ```

2. **Export your OpenRouter API key:**

   ```bash
   export OPENROUTER_API_KEY="your-api-key"
   ```

3. **Run the script:**

   ```bash
   python3 clanky_cli.py
   ```

> You can also alias it for quick access:
>
> ```bash
> alias clanky='python3 /full/path/to/clanky_cli.py'
> ```

---

## 🧭 Available Commands

| Command  | Function                                |
| -------- | --------------------------------------- |
| `/save`  | Save chat history to JSON and Markdown  |
| `/load`  | Interactively load a saved conversation |
| `/reset` | Clear current chat history              |
| `/model` | Display current model (user-defined)    |
| `/help`  | Show help and usage information         |
| `/exit`  | Quit the program                        |

---

## 🗂 Save File Handling

* Saved files are stored under:

  ```
  ~/your/file/path
  ```
* Each save generates two files:

  * `filename_YYYYMMDD_HHMMSS.json`
  * `filename_YYYYMMDD_HHMMSS.md`

You can load them interactively using arrow keys, and cancel at any time to return to the main chat.

---

## 🧪 Prompt Add-ons

* Add `#TABULATE` in your question to cleanly format tabular responses.
* Supports detection of code blocks in model responses (auto-stripped backticks).

---

## 🎨 Terminal Icons

This script uses ASCII/Nerd Font-friendly icons:

* `` Save
* `` JSON file
* `` Markdown file
* `` Cancel/Return

They are styled for minimalistic terminal UIs without color or emoji clutter.

---

## 🔐 Example API Key Setup

Use `.bashrc` or `.zshrc` for persistent API key:

```bash
export OPENROUTER_API_KEY="sk-or-...yourkey..."
```

---

## 👤 Author

* A clanker master
* Terminal enthusiast

---

Clanky is terminal-first and model-agnostic. Use it your way — with your favorite LLM.

> **Clanky AI – for the Clankers, by the Clankers.**
