# Highrise.bot (Python)

Unofficial Python SDK for [Highrise Virtual Reality](https://highrise.game)

1:1 with the official SDK on every core method, plus a set of tools it doesn't have: live room caching, uptime/latency/events_processed metrics, background loops, a dynamic command system with role-based permissions, local role persistence, auto message splitting, pause/resume, config-driven setup, a public WebApi client, and pagination support across the board using `async for-in` loops.

> [!NOTE]
> **Coming from the official SDK?** A few event hooks changed shape and `Message` is now a class with helper methods instead of a plain string. See the [Migration Guide](https://wk91p.github.io/highrise.bot.python/migration.html) in the docs before porting an existing bot.

## Installation

```bash
pip install "git+https://github.com/wk91p/highrise.bot.python.git"
```

## Quick start

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

## Documentation

Full guide, from installation to every hook, response, and tool: **[wk91p.github.io/highrise.bot.python](https://wk91p.github.io/highrise.bot.python)**