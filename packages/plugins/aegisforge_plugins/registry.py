from __future__ import annotations

from collections.abc import Callable


class PluginRegistry:
    def __init__(self) -> None:
        self._plugins: dict[str, Callable] = {}

    def register(self, name: str, func: Callable) -> None:
        self._plugins[name] = func

    def register_many(self, mapping: dict[str, Callable]) -> None:
        for name, func in mapping.items():
            self.register(name, func)

    def names(self) -> list[str]:
        return sorted(self._plugins)

    def get(self, name: str) -> Callable:
        return self._plugins[name]
