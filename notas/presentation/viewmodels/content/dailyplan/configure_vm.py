from dataclasses import dataclass


@dataclass
class ConfigureFieldUI:
    name: str
    label: str
    value: bool
    enabled: bool
    hint: str | None = None


@dataclass
class ConfigureSectionUI:
    title: str
    fields: list[ConfigureFieldUI]


@dataclass
class ConfigureVM:
    header: dict
    sections: list[ConfigureSectionUI]