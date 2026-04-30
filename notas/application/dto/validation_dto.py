from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class ValidationMetricDTO:
    metric: str
    target: float
    actual: float
    delta: float
    tolerance: float
    within_tolerance: bool
    status: str

    def as_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class DailyPlanValidationSummaryDTO:
    dailyplan_id: int
    dailyplan_name: str
    targets: dict
    actual: dict
    delta: dict
    tolerances: dict
    within_tolerance: bool
    metrics: list[ValidationMetricDTO]

    def as_dict(self) -> dict:
        data = asdict(self)
        data["metrics"] = [
            metric.as_dict()
            for metric in self.metrics
        ]
        return data