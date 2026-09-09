# Validator

`Validator` is a chainable input validator used internally throughout the SDK, every method on `self.highrise` and `self.webapi` builds its own checks from it before sending a request. Every method is a `@staticmethod`, raises `ValueError` on failure, and returns `Validator` on success so calls can be chained in one expression.

```python
Validator.required(message, "message").string(message, "message")
```

You won't normally call `Validator` directly in your own bot code, the SDK does it for you, but it's useful to know what it enforces since these are the errors you'll see surfaced through `response.error`.

If you do call it yourself, for example to validate your own command arguments, it behaves like a normal function: a failed check raises `ValueError` immediately, right where you called it. It's only inside the SDK's own request methods that this gets caught and turned into a response.

```python
try:
    Validator.string(user_input, "user_input")
except ValueError as e:
    await self.highrise.chat(str(e))
    return
```

## Type checks

```python
Validator.string(value, field)      # non-empty string
Validator.number(value, field)      # int or float, not bool
Validator.integer(value, field)     # int, not bool
Validator.boolean(value, field)     # bool
Validator.array(value, field)       # list or tuple
Validator.object(value, field)      # dict
Validator.callable(value, field)    # callable
Validator.instance_of(value, expected_type, field)
```

## Presence and shape

```python
Validator.required(value, field)                  # not None
Validator.non_empty_array(value, field)            # list/tuple, len > 0
Validator.min_length(value, minimum, field)        # string, len >= minimum
Validator.max_length(value, maximum, field)        # string, len <= maximum
Validator.max_items(value, maximum, field)         # list, len <= maximum
```

## Value constraints

```python
Validator.range(value, minimum, maximum, field)    # minimum <= value <= maximum
Validator.one_of(value, options, field)            # value in options
Validator.positive(value, field)                   # number > 0
Validator.non_negative(value, field)                # number >= 0
Validator.match(value, pattern, field)              # string matches a compiled regex Pattern
```

## Compound checks

Built for specific SDK use cases, each one chains several of the checks above:

```python
Validator.is_coordinates(x, y, z, facing)
# required + non_negative on x and z, required + number on y,
# required + string + one_of(FACING_DIRECTIONS) on facing

Validator.is_anchor(entity_id, anchor_ix)
# required + string on entity_id, required + non_negative on anchor_ix
```

## Error messages

Every failure names the exact field and rule that failed, for example:

```
message must be a non-empty string
facing must be one of: FrontRight, FrontLeft, BackRight, BackLeft
limit must be between 1 and 100
```

Since the SDK never lets these raise up to your bot code, see [Error Handling](../fundamentals/errors.md) for how validation failures actually surface through response objects instead.