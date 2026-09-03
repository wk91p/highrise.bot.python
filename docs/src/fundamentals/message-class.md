# The Message Class

Chat, whisper and direct hooks hand you a `message` argument. This page covers what it gives you beyond the raw text, mainly built-in command parsing.

## The basics

```python
async def on_chat(self, user, message):
    print(message.content)
```

`message.content` is the full text as sent, untouched.

## Built-in command parsing

The moment a `Message` is created, its content is split on whitespace and cached internally. That split powers three helper methods, so you don't have to write your own parsing for every command.

**`command()`**

Returns the first word of the message, the part you'd treat as the command name.

```python
async def on_chat(self, user, message):
    if message.command() == "!kick":
        ...
```

**`args(index=None)`**

Returns everything after the command. Call it with no arguments to get the full list, or pass an index to grab one specific argument.

```python
async def on_chat(self, user, message):
    # "!kick 5" -> command() == "!kick", args() == ["5"]
    if message.command() == "!kick":
        target = message.args(0)
        if target:
            await self.highrise.chat(f"Kicking {target}")
```

If the index is out of range, you get `None` back instead of an error, so you can check for missing arguments safely:

```python
reason = message.args(1)
if reason is None:
    await self.highrise.chat("Usage: !kick <user> <reason>")
    return
```

**`mentions(index=None)`**

Returns every word that starts with `@`, with the `@` stripped off. Same optional index behavior as `args()`.

```python
async def on_chat(self, user, message):
    # "!warn @someone being rude" -> mentions() == ["someone"]
    if message.command() == "!warn":
        target = message.mentions(0)
        if target:
            await self.highrise.chat(f"Warning issued to {target}")
```

## Putting it together

A small command handler using all three:

```python
async def on_chat(self, user, message):
    if message.command() == "!warn":

        target = message.mentions(0)
        reason = message.args(1)

        if not target or not reason:
            await self.highrise.chat("Usage: !warn @user <reason>")
            return

        await self.highrise.chat(f"{target} warned for: {reason}")
```

## What is next

Head to [Error Handling](./errors.md) to see how validation failures and request errors actually surface in your code.