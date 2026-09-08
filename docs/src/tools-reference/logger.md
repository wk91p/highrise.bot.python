# Logger

`Logger` is a utility used to configure clean, structured logs for your bot application. It outputs formatted logs directly to the console, complete with customized UTC timestamps and color-coded tags based on the logging severity level.

# Integration with BaseBot

The `BaseBot` class exposes a built-in `logger` property used by the SDK. Developers can choose to configure their own completely isolated loggers or seamlessly pass a configuration to manage and update the default SDK logger.

### Configuration via BotConfig

You can configure the SDK logger by feeding a `LoggerConfig` block inside your `BotConfig` directly into your bot instance.

```python
import asyncio
from highrise import BaseBot, BotConfig, LoggerConfig, LoggerLevel

class MyBot(BaseBot):
    async def on_start(self):
        # Accessing the pre-configured SDK logger property
        self.logger.info("Bot is initialized and ready.")

# Customizing the SDK logger through configuration parameters
config = BotConfig(
    logger = LoggerConfig(
        name = "MyCustomBotName",
        level = LoggerLevel.INFO,
        show_time = True
    )
)

# Pass the configuration into your bot class instance
bot = MyBot(config)
asyncio.run(bot.login(room_id, api_token))
```

# Configuration Blocks

### `LoggerConfig`
The parameters defined inside `LoggerConfig` dictate how the underlying SDK logging system initializes:

- `name`: The identifier string for the logger instance, defaulting to `"HighriseBot"`.
- `level`: The minimum severity threshold of messages to log, defaulting to `LoggerLevel.DEBUG`.
- `show_time`: Controls whether to prepend a customized UTC timestamp (`YYYY/MM/DD | HH:MM:SS`) to each log line, defaulting to `True`.

# Enum: LoggerLevel

An integer-based enumeration (`IntEnum`) that maps directly to Python’s native logging levels:

* `LoggerLevel.DEBUG`: Detailed information for diagnosing problems.
* `LoggerLevel.INFO`: Confirmation that things are working as expected.
* `LoggerLevel.WARNING`: An indication that something unexpected happened, or a problem is emerging.
* `LoggerLevel.ERROR`: Due to a more serious problem, the software has not been able to perform some function.
* `LoggerLevel.CRITICAL`: A serious error, indicating that the program itself may be unable to continue running.

# Functions

Now we will explain what the main setup function does and what it returns.

## setup_logger()
Configures a console stream handler, injects custom formatting logic, clears any pre-existing duplicate handlers on that channel name, and returns the active logger instance.

```python
from highrise import setup_logger, LoggerLevel

# Setup your own standalone logger separate from the BotConfig ecosystem
custom_logger = setup_logger(
    name="StandaloneLogger", 
    level=LoggerLevel.WARNING, 
    show_time=True
)

custom_logger.warning("Standalone warning event captured.")
```
* **Returns**: `logging.Logger`
