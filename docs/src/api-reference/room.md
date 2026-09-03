# Room

Methods for reading and managing room-level state: who's in the room, and their moderator/designer privileges.

## get_room_users()

```python
async def get_room_users(self) -> GetRoomUsersResponse
```

Fetches every user currently in the room, along with their positions.

```python
response = await self.highrise.get_room_users()

for user, position in response.content:
    print(f"{user.username} at {position}")
```

### GetRoomUsersResponse body
The list of users in the room, alongside their positions.

```python
class GetRoomUsersResponse(BaseResponse):
    content: list[tuple[User, Position | AnchorPosition]]
```

## get_room_privilege()

```python
async def get_room_privilege(self, user_id: str) -> GetRoomPrivilegeResponse
```

Fetches the room privilege for a given user, whether they have moderator and/or designer access.

```python
response = await self.highrise.get_room_privilege(user.id)
```

### GetRoomPrivilegeResponse body
The room privileges for a user

```python
class GetRoomPrivilegeResponse(BaseResponse):
    moderator: bool | None
    designer: bool | None
```

## is_moderator() / is_designer()

```python
async def is_moderator(self, user_id: str) -> bool
async def is_designer(self, user_id: str) -> bool
```

Convenience checks built on `get_room_privilege()`. Return `True`/`False` directly instead of a response object.

```python
async def on_chat(self, user, message):
    if message.command() == "!mod-only":
        if not await self.highrise.is_moderator(user.id):
            await self.highrise.chat("Mods only!")
            return
```

## change_room_privilege()

```python
async def change_room_privilege(self, user_id: str, permissions: RoomPermissions) -> AcknowledgementResponse
```

Sets a user's room privileges directly. `RoomPermissions` takes optional `moderator` and `designer` booleans, only the fields you set are changed.

```python
await self.highrise.change_room_privilege(user.id, RoomPermissions(moderator=True, designer=False))
```

You'll usually reach for the shortcuts below instead.

## Privilege shortcuts

All of these wrap `change_room_privilege()` internally:

```python
await self.highrise.add_moderator(user.id)
await self.highrise.remove_moderator(user.id)
await self.highrise.add_designer(user.id)
await self.highrise.remove_designer(user.id)
```