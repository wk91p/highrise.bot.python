from typing import Any, Iterable, Type, Pattern

from highrise.constants import FACING_DIRECTIONS

class Validator:
    """Chainable input validator for SDK-wide argument checking.

    Every method raises ValueError on failure and returns self,
    so calls can be chained together in a single expression.
    """

    def string(self, value: Any, field: str) -> "Validator":
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field} must be a non-empty string")
        return self

    def number(self, value: Any, field: str) -> "Validator":
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{field} must be a number")
        return self

    def callable(self, value: Any, field: str) -> "Validator":
        if not callable(value):
            raise ValueError(f"{field} must be callable")
        return self

    def required(self, value: Any, field: str) -> "Validator":
        if value is None:
            raise ValueError(f"{field} is required")
        return self

    def range(self, value: Any, minimum: float, maximum: float, field: str) -> "Validator":
        if value < minimum or value > maximum:
            raise ValueError(f"{field} must be between {minimum} and {maximum}")
        return self

    def one_of(self, value: Any, options: Iterable[Any], field: str) -> "Validator":
        if value not in options:
            raise ValueError(f"{field} must be one of: {', '.join(map(str, options))}")
        return self

    def boolean(self, value: Any, field: str) -> "Validator":
        if not isinstance(value, bool):
            raise ValueError(f"{field} must be a boolean")
        return self

    def array(self, value: Any, field: str) -> "Validator":
        if not isinstance(value, (list, tuple)):
            raise ValueError(f"{field} must be an array")
        return self

    def non_empty_array(self, value: Any, field: str) -> "Validator":
        if not isinstance(value, (list, tuple)) or len(value) == 0:
            raise ValueError(f"{field} must be a non-empty array")
        return self

    def min_length(self, value: Any, minimum: int, field: str) -> "Validator":
        if not isinstance(value, str) or len(value) < minimum:
            raise ValueError(f"{field} must be at least {minimum} characters")
        return self

    def max_items(self, value: Any, maximum: int, field: str) -> "Validator":
        if not isinstance(value, list) or len(value) > maximum:
            raise ValueError(f"{field} must have at most {maximum} items")
        return self

    def max_length(self, value: Any, maximum: int, field: str) -> "Validator":
        if not isinstance(value, str) or len(value) > maximum:
            raise ValueError(f"{field} must be at most {maximum} characters")
        return self

    def integer(self, value: Any, field: str) -> "Validator":
        if not isinstance(value, int) or isinstance(value, bool):
            raise ValueError(f"{field} must be an integer")
        return self

    def positive(self, value: Any, field: str) -> "Validator":
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
            raise ValueError(f"{field} must be a positive number")
        return self

    def non_negative(self, value: Any, field: str) -> "Validator":
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
            raise ValueError(f"{field} must be 0 or greater")
        return self

    def instance_of(self, value: Any, expected_type: Type, field: str) -> "Validator":
        if not isinstance(value, expected_type):
            raise ValueError(f"{field} must be an instance of {expected_type.__name__}")
        return self

    def match(self, value: Any, pattern: Pattern, field: str) -> "Validator":
        if not isinstance(value, str) or not pattern.search(value):
            raise ValueError(f"{field} does not match the required pattern")
        return self

    def object(self, value: Any, field: str) -> "Validator":
        if not isinstance(value, dict):
            raise ValueError(f"{field} must be a plain object")
        return self

    def is_coordinates(self, x: Any, y: Any, z: Any, facing: Any) -> "Validator":
        (
            self.required(x, "x").non_negative(x, "x")
            .required(y, "y").number(y, "y")
            .required(z, "z").non_negative(z, "z")
            .required(facing, "facing")
            .string(facing, "facing")
            .one_of(facing, FACING_DIRECTIONS, "facing")
        )
        return self

    def is_anchor(self, entity_id: Any, anchor_ix: Any) -> "Validator":
        (
            self.required(entity_id, "entity_id").string(entity_id, "entity_id")
            .required(anchor_ix, "anchor_ix").non_negative(anchor_ix, "anchor_ix")
        )
        return self