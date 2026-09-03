# Installation

Let's get `highrise.bot` installed and your project set up. This takes about five minutes.

## Requirements

- Python 3.10 or higher
- pip

Check your version:

```bash
python --version
```

`Python 3.11.4` or similar means you're good. If you get an error or an older version, grab the latest from [python.org](https://www.python.org/downloads/).

## Create your project

```bash
mkdir my-bot
cd my-bot
python -m venv venv
```

`mkdir my-bot` makes a folder for your bot. `cd my-bot` moves into it. `python -m venv .venv` sets up an isolated virtual environment named `.venv` so your bot's dependencies don't clash with anything else on your system.

Activate it:

```bash
# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

Your terminal prompt should now show `(venv)` at the start of the line. That means the environment is active.

## Install the SDK

```bash
pip install "git+https://github.com/wk91p/highrise.bot.python.git"
```

That's it. You're ready to write your first bot, move to the next page to continue!.