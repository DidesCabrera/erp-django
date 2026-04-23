from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class HeaderActionVM:
    key: str
    label: str
    url: str
    method: str = "get"
    group: str = "primary"
    icon: Optional[str] = None
    is_back: bool = False
    order: int = 0


@dataclass
class HeaderVM:
    title: str = ""
    actions: List[HeaderActionVM] = field(default_factory=list)