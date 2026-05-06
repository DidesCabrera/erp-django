from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class MCPToolSpec:
    name: str
    description: str
    api_path: str
    input_schema: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class MCPToolCallResult:
    ok: bool
    data: dict[str, Any]
    error: dict[str, Any] | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "data": self.data,
            "error": self.error,
        }