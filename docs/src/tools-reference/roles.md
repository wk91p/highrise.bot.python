# Roles

`Roles` is a built-in tool to manage `mod`, `owner` and custom roles added by the developers, it has disk persistence loading and saving roles during runtime with a configurable intervals using `RolesConfig` in `BotConfig`, useful for role-based commands.

> [!IMPORTANT]
> `mod` and `owner` uses `WebApi` room endpoint to fetch the room privileges during startup if any error happend during the process, it will just log a warning.

# Configration

You can configure `Roles` using these parameters:

```python
import asyncio
from highrise import BaseBot, BotConfig, RolesConfig

class MyBot(BaseBot): ...

config = BotConfig(
    roles = RolesConfig(
        path = "./jsons/roles.json",
        autosave_interval = 600.0
    )
)

bot = MyBot(config)

asyncio.run(bot.login(room_id, api_token))
```

- `path`: A path for the json file location where it will be loaded from and saved to, default to `"./jsons/roles.json"`.

- `autosave_interval`: The time in seconds between each automatic save of the roles data to the JSON file, defaulting to `600.0` (10 minutes).

# Manual Setup

To use the `Roles` class manually or integrate it into your code structure, initialize it by passing an optional storage path.

```python
from pathlib import Path
from highrise import Roles

# Initialize with the default path ("./jsons/roles.json")
roles_manager = Roles()

# Custom initialization with a specific string path
roles_manager = Roles(path="./data/custom_roles.json")

# Custom initialization using a Path object
roles_manager = Roles(path=Path("/var/data/roles.json"))
```

### Notes
- **Automatic Directory Creation:** The class automatically creates any missing parent directories (like `./jsons/` or `./data/`) during initialization.
- **Graceful Fallbacks:** If the target JSON file does not exist, is empty, or is unreadable, the class automatically initializes with empty default values for the default `mod` and `owner` groups without raising an exception.
- **Auto-Save on Shutdown:** The class registers itself with Python's `atexit` module, ensuring your data is safely saved to disk when the program closes cleanly.


# Methods

Now we will explain what each method inside `Roles` do and what it returns.

## add_role()
Adds a role if it does not exist, then assigns it to the given user.

```python
# Create a new VIP role and add a user to it
bot.roles.add_role("vip", "user_12345")
```
* **Returns**: `None`

## `remove_role(role: str, user_id: str)`
Removes a user from a specific role. Does nothing if the user or role does not exist.

```python
# Remove a user from the VIP role
bot.roles.remove_role("vip", "user_12345")
```
* **Returns**: `None`

## has_role()
Checks whether a user has the given role.

```python
has_vip = bot.roles.has_role("user_12345", "vip")

if has_vip:
    print("User is a VIP!")
```
* **Returns**: `bool`

## has_any_role()
Checks whether a user has at least one of the roles in the provided list.

```python
has_any_role = bot.roles.has_any_role("user_12345", ["mod", "owner", "admin"])

if has_any_role:
    print("User has staff privileges.")
```
* **Returns**: `bool`

## has_all_roles()
Checks whether a user has every single role in the provided list.

```python
has_all_roles = bot.roles.has_all_roles("user_12345", ["mod", "verified"])

if has_all_roles:
    print("User is both a moderator and verified.")
```
* **Returns**: `bool`

## get_roles()
Retrieves all roles currently assigned to a specific user.

```python
user_roles = bot.roles.get_roles("user_12345")
# Output: ['mod', 'vip']
```
* **Returns**: `list[str]`

## get_users()
Retrieves all user IDs assigned to a specific role.

```python
mod_list = bot.roles.get_users("mod")
# Output: ['user_12345', 'user_67890']
```
* **Returns**: `list[str]`

## is_mod()
A convenience method to check if a user has the `mod` role.

```python
is_mod = bot.roles.is_mod("user_12345")

if is_mod:
    print("This user is a moderator.")
```
* **Returns**: `bool`

## is_owner()
A convenience method to check if a user has the `owner` role.

```python
is_owner = bot.roles.is_owner("user_12345")

if is_owner:
    print("This user is the room owner.")
```
* **Returns**: `bool`

## delete_role()
Deletes an entire role from the system, automatically removing all users assigned to it.

```python
# Completely remove the VIP role from the system
bot.roles.delete_role("vip")
```
* **Returns**: `None`

## list_roles()
Retrieves the names of all defined roles.

```python
all_roles = bot.roles.list_roles()
# Output: ['mod', 'owner', 'vip']
```
* **Returns**: `list[str]`

## save()
Manually forces an atomic save of all current roles data to the JSON file.

```python
# Force immediate save after a critical update
bot.roles.save()
```
* **Returns**: `None`
