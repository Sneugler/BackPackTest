from __future__ import annotations

import json
from dataclasses import MISSING, asdict, dataclass, field, fields
from enum import Enum
from typing import Any, get_args, get_origin, get_type_hints


def Field(default=MISSING, default_factory=MISSING, **_: Any):
    if default_factory is not MISSING:
        return field(default_factory=default_factory)
    if default is MISSING:
        return field()
    return field(default=default)


class BaseModel:
    def __init_subclass__(cls, **kwargs: Any):
        super().__init_subclass__(**kwargs)
        dataclass(cls, kw_only=True)

    @classmethod
    def _convert_value(cls, annotation: Any, value: Any) -> Any:
        origin = get_origin(annotation)
        if origin is None:
            if value is None:
                return None
            if isinstance(annotation, type) and issubclass(annotation, BaseModel):
                return value if isinstance(value, annotation) else annotation(**value)
            if isinstance(annotation, type) and issubclass(annotation, Enum):
                return value if isinstance(value, annotation) else annotation(value)
            return value
        if origin is list:
            item_type = get_args(annotation)[0] if get_args(annotation) else Any
            return [cls._convert_value(item_type, item) for item in (value or [])]
        if origin is dict:
            return value or {}
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if len(args) == 1:
            return cls._convert_value(args[0], value)
        return value

    def __post_init__(self):
        hints = get_type_hints(self.__class__)
        for item in fields(self):
            annotation = hints.get(item.name, item.type)
            setattr(self, item.name, self._convert_value(annotation, getattr(self, item.name)))

    def model_dump(self, mode: str | None = None) -> dict[str, Any]:
        def convert(obj: Any):
            if isinstance(obj, BaseModel):
                return obj.model_dump(mode=mode)
            if isinstance(obj, Enum):
                return obj.value
            if isinstance(obj, list):
                return [convert(i) for i in obj]
            if isinstance(obj, dict):
                return {k: convert(v) for k, v in obj.items()}
            if hasattr(obj, 'isoformat') and mode == 'json':
                try:
                    return obj.isoformat()
                except Exception:
                    return obj
            return obj
        return {k: convert(v) for k, v in asdict(self).items()}

    def model_dump_json(self) -> str:
        return json.dumps(self.model_dump(mode='json'))

    @classmethod
    def model_validate(cls, data: dict[str, Any]):
        return cls(**data)

    @classmethod
    def model_validate_json(cls, data: str):
        return cls.model_validate(json.loads(data))
