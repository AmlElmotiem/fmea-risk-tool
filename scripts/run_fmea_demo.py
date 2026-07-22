"""Demo FMEA analysis of a rodless pneumatic cylinder (the same component
type from the CAD portfolio project), showing the tool end to end.

Run: python scripts/run_fmea_demo.py
"""

from __future__ import annotations

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from fmea_tool import FailureMode, FMEAAnalysis, plot_risk_chart, write_csv

RESULTS_DIR = Path(__file__).resolve().parents[1] / "results"


def build_analysis() -> FMEAAnalysis:
    analysis = FMEAAnalysis(title="Kolbenstangenloser Pneumatikzylinder")

    analysis.add(FailureMode(
        component="Kolbendichtung",
        function="Abdichtung der beiden Druckkammern",
        failure_mode="Dichtungsverschleiß/-riss",
        effect="Luftverlust zwischen den Kammern, Druckabfall, reduzierte Kraftübertragung",
        severity=7, occurrence=4, detection=5,
        recommended_action="Regelmäßige Dichtungsinspektion; verschleißfesteres Dichtungsmaterial prüfen",
    ))
    analysis.add(FailureMode(
        component="Führungsschiene",
        function="Präzise Linearführung des externen Schlittens",
        failure_mode="Verschleiß der Führungsschiene",
        effect="Erhöhtes mechanisches Spiel, ungenaue Positionierung",
        severity=6, occurrence=5, detection=6,
        recommended_action="Schmierintervall verkürzen; Verschleißgrenzwerte definieren und prüfen",
    ))
    analysis.add(FailureMode(
        component="Magnetkopplung",
        function="Kraftübertragung vom Kolben auf den externen Schlitten",
        failure_mode="Entkopplung bei Überlast",
        effect="Plötzlicher Kontrollverlust; Schlitten bleibt stehen, Kolben läuft weiter",
        severity=8, occurrence=2, detection=3,
        recommended_action="Überlast-Sensorik ergänzen; maximale Prozesskraft klar spezifizieren",
    ))
    analysis.add(FailureMode(
        component="Endlagendämpfung",
        function="Sanftes Abbremsen vor Erreichen der Endlage",
        failure_mode="Dämpfungsventil verstopft",
        effect="Harter mechanischer Anschlag, erhöhter Verschleiß, Beschädigungsrisiko",
        severity=5, occurrence=3, detection=4,
        recommended_action="Wartungsintervall für Dämpfungsventile festlegen",
    ))
    analysis.add(FailureMode(
        component="Druckluftanschluss",
        function="Zuführung der Druckluft von der Versorgungsleitung",
        failure_mode="Undichte Verschraubung",
        effect="Leistungsverlust, erhöhter Luftverbrauch",
        severity=3, occurrence=6, detection=7,
        recommended_action="Drehmomentvorgabe für Verschraubung dokumentieren und prüfen",
    ))
    analysis.add(FailureMode(
        component="Positionssensor",
        function="Erfassung der Schlittenposition für die Steuerung",
        failure_mode="Signaldrift des Reed-Sensors",
        effect="Steuerung erhält falsche Positionsrückmeldung, Fehlpositionierung möglich",
        severity=6, occurrence=3, detection=6,
        recommended_action="Sensor-Plausibilisierung in Steuerung ergänzen; Kalibrierintervall festlegen",
    ))
    return analysis


def main() -> None:
    analysis = build_analysis()

    print(f"=== FMEA: {analysis.title} ===\n")
    for fm in analysis.ranked():
        print(f"[{fm.risk_level:>8}] RPN={fm.rpn:>3}  {fm.component}: {fm.failure_mode}")

    critical = analysis.above_threshold(rpn_threshold=100)
    print(f"\n{len(critical)} von {len(analysis.failure_modes)} Fehlerarten über dem Schwellenwert (RPN >= 100) -- benötigen priorisierte Maßnahmen.")

    RESULTS_DIR.mkdir(exist_ok=True)
    csv_path = RESULTS_DIR / "fmea_report.csv"
    write_csv(analysis, csv_path)
    print(f"\nWrote {csv_path}")

    chart_path = RESULTS_DIR / "fmea_risk_chart.png"
    plot_risk_chart(analysis, chart_path)
    print(f"Wrote {chart_path}")


if __name__ == "__main__":
    main()
