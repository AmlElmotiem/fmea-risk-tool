"""Core FMEA (Failure Mode and Effects Analysis) data model.

Each FailureMode represents one way a component or function can fail.
Severity, occurrence, and detection are rated 1-10 (10 = worst), per
standard FMEA practice. Their product is the Risk Priority Number
(RPN), used to prioritize which failure modes need action first.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class FailureMode:
    component: str
    function: str
    failure_mode: str
    effect: str
    severity: int
    occurrence: int
    detection: int
    recommended_action: str = ""

    def __post_init__(self) -> None:
        for name, value in [
            ("severity", self.severity),
            ("occurrence", self.occurrence),
            ("detection", self.detection),
        ]:
            if not (1 <= value <= 10):
                raise ValueError(f"{name} must be between 1 and 10, got {value}")

    @property
    def rpn(self) -> int:
        """Risk Priority Number: severity x occurrence x detection.

        Ranges from 1 (negligible risk) to 1000 (most critical)."""
        return self.severity * self.occurrence * self.detection

    @property
    def risk_level(self) -> str:
        """A simple, commonly used RPN banding for quick triage."""
        if self.rpn >= 200:
            return "CRITICAL"
        if self.rpn >= 100:
            return "HIGH"
        if self.rpn >= 40:
            return "MEDIUM"
        return "LOW"


@dataclass
class FMEAAnalysis:
    title: str
    failure_modes: list[FailureMode] = field(default_factory=list)

    def add(self, failure_mode: FailureMode) -> None:
        self.failure_modes.append(failure_mode)

    def ranked(self) -> list[FailureMode]:
        """Failure modes sorted highest-risk first -- the order a real
        FMEA review meeting would work through them."""
        return sorted(self.failure_modes, key=lambda fm: fm.rpn, reverse=True)

    def above_threshold(self, rpn_threshold: int = 100) -> list[FailureMode]:
        """Failure modes that need action now, per a chosen RPN cutoff."""
        return [fm for fm in self.ranked() if fm.rpn >= rpn_threshold]
