# Installation

Let's get `highrise.bot` installed and your project set up. This takes about five minutes.

## Requirements

- Python 3.10 or higher
- pip
- A code editor (this guide uses [VS Code](https://code.visualstudio.com/), but any editor works)

Check your version:

```bash
python --version
```

`Python 3.11.4` or similar means you're good. If you get an error or an older version, grab the latest from [python.org](https://www.python.org/downloads/).

## Set up your editor

If you don't already have one, download [VS Code](https://code.visualstudio.com/) and install it. Once it's open, install the official Python extension: click the Extensions icon in the sidebar (or press `Ctrl+Shift+X` / `Cmd+Shift+X` on macOS), search for `Python`, and install the one published by `Microsoft`. This gives you syntax highlighting, autocomplete, and lets VS Code recognize your virtual environment automatically once it's created.

## Create your project

First, make a folder for your bot somewhere on your computer, name it whatever you like, for example `my-bot`. Open `VS Code`, then `File > Open Folder`, and select that folder. VS Code now treats it as your project.

Next, open a terminal inside VS Code: `Terminal > New Terminal` from the top menu, or the shortcut `` Ctrl + ` `` (`` Cmd + ` `` on macOS). A terminal panel opens at the bottom, already pointed at your project folder, no need to `cd` anywhere.

In that terminal, create a virtual environment:

```bash
python -m venv venv
```

This sets up an isolated environment named `venv` inside your project folder, so your bot's dependencies don't clash with anything else on your system.

Activate it:

```bash
# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

Your terminal prompt should now show `(venv)` at the start of the line. That means the environment is active.

Now tell VS Code to use this environment: open the command palette (`Ctrl+Shift+P` / `Cmd+Shift+P` on macOS), run `Python: Select Interpreter`, and choose the one inside your `venv` folder. From now on, VS Code's integrated terminal and any file you run will use this environment automatically.

## Install the SDK

```bash
pip install "git+https://github.com/wk91p/highrise.bot.python.git"
```

That's it. You're ready to write your first bot, move to the next page to continue!