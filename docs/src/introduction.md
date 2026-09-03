# Highrise bot guide book (Python)

`highrise.bot` is the first unofficial Python SDK for Highrise. It gives you a full toolkit for writing bots: structured events, built-in input validation, a caching layer, and response objects that are ready to use out of the box.

> [!IMPORTANT]
> Most methods on `self.highrise` map directly to the official API, with a few modifications and removals to improve code quality.

It was built around a few goals:

**Performance.** The dispatcher has been stress-tested at scale, handling large rooms and tens of thousands of events with few milliseconds per-event overhead and stable memory.

**Validation.** Every request is checked before it goes out, so bad input gets caught immediately with a clear error instead of failing silently or crashing your bot.

**Lightweight.** No heavy dependency tree. It installs fast and stays out of your way.

**Connection control.** You get fine-grained control over reconnects, timeouts, and lifecycle events instead of a black-box connection you can't inspect.

Every action has a clean API. Responses are fully structured and ready to use with built-in methods. You spend your time building features.

All it takes is a few lines to spawn a bot in your room:

```python
import asyncio
from highrise import BaseBot

class MyBot(BaseBot):
    async def on_chat(self, user, message):
        print(f"{user.username}: {message.content}")

if __name__ == "__main__":
    ROOM_ID = "put_your_room_id_here"
    API_TOKEN = "put_your_bot_token_here"

    bot = MyBot()

    try:
        asyncio.run(bot.login(ROOM_ID, API_TOKEN))
    except KeyboardInterrupt:
        print("\nBot stopped manually by user.")
```

## What we need ?

Three things before we get started.

- **Python 3.10 or higher**

    This is the runtime that executes your bot code. Head to [python.org](https://www.python.org/downloads/) and download the latest version. If you already have Python installed, open your terminal and run `python --version` to check.

- **A bot token**

    This is the key that proves to Highrise that your bot is allowed to connect. Go to the [Highrise developer portal](https://create.highrise.game/dashboard/credentials/api-keys) and login with your highrise account, create a new bot, give it a name you will recognize, generate a new token from the 3 dots next to it, and copy the token it generates. Keep it somewhere safe because you will need it in a moment.

- **Your room ID**

    This tells the bot which room to live in. Open the [Rooms tab](https://create.highrise.game/dashboard/creations?type=rooms) in the developer portal, find the room you want, click the three dots next to it, and copy the room ID.

Got all three? Head to [Installation](./getting-started/installation.md) and let's get your bot running.