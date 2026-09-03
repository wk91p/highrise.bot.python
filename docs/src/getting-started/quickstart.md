# Quick Start

Your SDK is installed. Now let's write a bot and understand every piece of it, including how to configure its behavior.

## Writing your first bot

Create a file called `mybot.py`:

```python
import asyncio
from highrise import BaseBot

class MyBot(BaseBot):
    async def on_ready(self):
        print("Online!")
        await self.highrise.chat("Hello everyone!")

    async def on_chat(self, user, message):
        if message.command() == "!ping":
            await self.highrise.chat("Pong! 🏓")

if __name__ == "__main__":
    ROOM_ID = "paste_your_room_id_here"
    API_TOKEN = "paste_your_bot_token_here"

    bot = MyBot()

    try:
        asyncio.run(bot.login(ROOM_ID, API_TOKEN))
    except KeyboardInterrupt:
        print("\nBot stopped manually by user.")
```

Run it:

```bash
python mybot.py
```

Go to your room. Your bot should be online and respond to `!ping`.

## Configuring your bot with BotConfig

Every bot accepts an optional `BotConfig` object. It controls reconnection behavior, logging, automatic data fetching, and role persistence, so you don't have to hardcode any of it yourself.

```python
from highrise import BaseBot
from highrise.config import BotConfig, ConnectionConfig, LoggerConfig, AutoFetchConfig, RolesConfig

config = BotConfig(
    connection=ConnectionConfig(
        keepalive_delay=15,
        min_reconnect_delay=5.0,
        max_reconnect_delay=30.0,
        reconnect_backoff_factor=2.0,
        max_reconnect_attempts=None,
    ),
    logger=LoggerConfig(
        name="MyBot",
        level=LoggerLevel.DEBUG,
        show_time=True,
    ),
    auto_fetch=AutoFetchConfig(
        room_users=False,
        direct_message=False,
    ),
    roles=RolesConfig(
        path="./jsons/roles.json",
        autosave_interval=600.0,
    ),
)

bot = MyBot(config=config)
```

`BotConfig` is a dataclass made up of four smaller dataclasses. Every field has a sensible default, so you only need to set the ones you actually want to change.

### ConnectionConfig

Controls how the bot manages its WebSocket connection.

- `keepalive_delay` - seconds between keepalive pings sent to keep the connection alive. Default `15`.
- `min_reconnect_delay` - shortest wait, in seconds, before the first reconnect attempt. Default `5.0`.
- `max_reconnect_delay` - longest wait, in seconds, a reconnect attempt will ever back off to. Default `30.0`.
- `reconnect_backoff_factor` - multiplier applied to the delay after each failed attempt, so retries space out over time instead of hammering the server. Default `2.0`.
- `max_reconnect_attempts` - how many times the bot will try reconnecting before giving up. `None` means retry forever.

### LoggerConfig

Controls what the built-in logger looks like.

- `name` - the prefix shown after timestamp in every log line, so you can tell bots apart if you run more than one. Default `"HighriseBot"`.
- `level` - the minimum severity that gets printed, using `LoggerLevel` (e.g. `DEBUG`, `INFO`). Default `LoggerLevel.DEBUG`.
- `show_time` - whether each log line includes a timestamp. Default `True`.

```py
[time] [name] [level] - message

[2026/09/01 | 09:21:52] - [HighriseBot] - [INFO] - Successfully connected to Highrise!
```

### AutoFetchConfig

Controls what the bot fetches automatically on connect, so you don't have to request it yourself.

- `room_users` - automatically fetch and cache the current room's user list. Default `False`.
- `direct_message` - automatically fetch direct message conversations. Default `False`.

### RolesConfig

Controls how the bot's role system is persisted to disk.

- `path` - where role data is saved and loaded from. Default `"./jsons/roles.json"`.
- `autosave_interval` - how often, in seconds, roles are automatically saved. Default `600.0` => 10 min.

## What is next ?

Head to the [Fundamentals](../fundamentals/bot-class.md) section to see how the bot class, hooks, and responses fit together, for a better understanding of the SDK's nature.