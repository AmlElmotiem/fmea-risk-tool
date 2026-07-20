"""Generates a structured report (table + chart) from an FMEAAnalysis."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from .model import FMEAAnalysis


def to_dataframe(analysis: FMEAAnalysis) -> pd.DataFrame:
    rows = [
        {
            "Komponente": fm.component,
            "Funktion": fm.function,
            "Fehlerart": fm.failure_mode,
            "Auswirkung": fm.effect,
            "S": fm.severity,
            "A": fm.occurrence,
            "E": fm.detection,
            "RPN": fm.rpn,
            "Risiko": fm.risk_level,
            "Empfohlene Maßnahme": fm.recommended_action,
        }
        for fm in analysis.ranked()
    ]
    return pd.DataFrame(rows)


def write_csv(analysis: FMEAAnalysis, path: Path) -> None:
    df = to_dataframe(analysis)
    df.to_csv(path, index=False)


def plot_risk_chart(analysis: FMEAAnalysis, path: Path) -> None:
    ranked = analysis.ranked()
    labels = [fm.failure_mode for fm in ranked]
    rpns = [fm.rpn for fm in ranked]
    colors = [
        "#8b1e1e" if fm.rpn >= 200 else "#b8631e" if fm.rpn >= 100 else "#c9a227" if fm.rpn >= 40 else "#2f7a4f"
        for fm in ranked
    ]

    fig, ax = plt.subplots(figsize=(9, max(3, 0.5 * len(ranked))))
    ax.barh(labels, rpns, color=colors)
    ax.invert_yaxis()
    ax.axvline(100, color="#444444", linestyle="--", linewidth=1, label="Schwellenwert (RPN=100)")
    ax.set_xlabel("Risikoprioritätszahl (RPN = Schweregrad x Auftreten x Entdeckung)")
    ax.set_title(f"FMEA-Risikoanalyse: {analysis.title}")
    ax.legend(loc="lower right")
    fig.tight_layout()

    path.parent.mkdir(exist_ok=True)
    fig.savefig(path, dpi=150)
