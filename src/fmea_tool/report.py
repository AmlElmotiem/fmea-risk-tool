"""Generates a structured report (table + chart) from an FMEAAnalysis."""

# Erlaubt es, Klassen-Typen zu nutzen, bevor sie im Code definiert sind
from __future__ import annotations

# Importiert 'Path' für den sicheren Umgang mit Datei-Pfaden (Ordnerstrukturen)
from pathlib import Path

# Importiert die Matplotlib-Bibliothek, um Grafiken und Diagramme zu zeichnen
import matplotlib.pyplot as plt
# Importiert Pandas, um Daten in Tabellen (DataFrames) zu speichern und als CSV zu exportieren
import pandas as pd

# Importiert die FMEA-Logik aus der Nachbardatei 'model.py'
from .model import FMEAAnalysis


def to_dataframe(analysis: FMEAAnalysis) -> pd.DataFrame:
    """
    Diese Funktion nimmt alle FMEA-Daten und wandelt sie in eine strukturierte
    Pandas-Tabelle (DataFrame) um, damit Python sie weiterverarbeiten kann.
    """
    # Eine Schleife (List Comprehension), die jede Fehlermöglichkeit (fm) durchläuft
    # 'analysis.ranked()' sorgt dafür, dass die Fehler bereits nach der höchsten RPN sortiert sind
    rows = [
        {
            "Komponente": fm.component,
            "Funktion": fm.function,
            "Fehlerart": fm.failure_mode,
            "Auswirkung": fm.effect,
            "S": fm.severity,          # S = Schweregrad
            "A": fm.occurrence,        # A = Auftretenswahrscheinlichkeit
            "E": fm.detection,         # E = Entdeckungswahrscheinlichkeit
            "RPN": fm.rpn,             # RPN = Risikoprioritätszahl (S x A x E)
            "Risiko": fm.risk_level,   # Automatische Einstufung (z.B. HIGH, MEDIUM)
            "Empfohlene Maßnahme": fm.recommended_action,
        }
        for fm in analysis.ranked()
    ]
    # Wandelt die Liste von Wörterbüchern (Dicts) in eine echte Pandas-Tabelle um
    return pd.DataFrame(rows)


def write_csv(analysis: FMEAAnalysis, path: Path) -> None:
    """
    Diese Funktion nimmt die FMEA-Tabelle und speichert sie als 
    echte Excel-kompatible CSV-Datei auf der Festplatte ab.
    """
    # 1. Ruft die obere Funktion auf, um die Tabelle zu erstellen
    df = to_dataframe(analysis)
    # 2. Speichert die Tabelle als CSV-Datei am angegebenen Pfad.
    # index=False verhindert, dass eine extra Spalte mit Zeilennummern (0, 1, 2...) erstellt wird.
    df.to_csv(path, index=False)


def plot_risk_chart(analysis: FMEAAnalysis, path: Path) -> None:
    """
    Diese Funktion zeichnet ein wunderschönes, farbcodiertes Balkendiagramm.
    Es zeigt dem Management sofort visuell, wo die größten Gefahren liegen.
    """
    # Holt die nach Risiko sortierte Liste der Fehler
    ranked = analysis.ranked()
    
    # Erstellt die Beschriftungen für die Y-Achse (die Namen der Fehlerarten)
    labels = [fm.failure_mode for fm in ranked]
    # Erstellt die Längen der Balken (die berechneten RPN-Zahlen)
    rpns = [fm.rpn for fm in ranked]
    
    # AUTOMATISCHE FARBCODIERUNG: JEDER BALKEN BEKOMMT EINE FARBE JE NACH RPN-WERT:
    # RPN >= 200 -> Dunkelrot (#8b1e1e) | Kritisch
    # RPN >= 100 -> Orange (#b8631e)    | Hoch
    # RPN >= 40  -> Gelb (#c9a227)      | Mittel
    # Alles darunter -> Grün (#2f7a4f)  | Niedrig
    colors = [
        "#8b1e1e" if fm.rpn >= 200 else "#b8631e" if fm.rpn >= 100 else "#c9a227" if fm.rpn >= 40 else "#2f7a4f"
        for fm in ranked
    ]

    # Erstellt das Diagramm-Fenster. 
    # Die Höhe des Diagramms passt sich dynamisch an die Anzahl der Fehler an (0.5 * Anzahl)
    fig, ax = plt.subplots(figsize=(9, max(3, 0.5 * len(ranked))))
    
    # Zeichnet ein horizontales Balkendiagramm (barh = bar horizontal)
    # labels = Y-Achse, rpns = X-Achse (Länge des Balkens), color = die definierte Farbe
    ax.barh(labels, rpns, color=colors)
    
    # Dreht die Y-Achse um, damit das höchste Risiko ganz oben steht
    ax.invert_yaxis()
    
    # Zeichnet eine vertikale, gestrichelte graue Linie bei RPN=100 als optische Warngrenze
    ax.axvline(100, color="#444444", linestyle="--", linewidth=1, label="Schwellenwert (RPN=100)")
    
    # Beschriftet die X-Achse am unteren Rand
    ax.set_xlabel("Risikoprioritätszahl (RPN = Schweregrad x Auftreten x Entdeckung)")
    # Setzt die Hauptüberschrift des Diagramms (nutzt den Titel des FMEA-Projekts)
    ax.set_title(f"FMEA-Risikoanalyse: {analysis.title}")
    # Blendet die Legende für den Schwellenwert unten rechts ein
    ax.legend(loc="lower right")
    
    # Optimiert die Abstände, damit keine Texte abgeschnitten werden
    fig.tight_layout()

    # Erstellt den Zielordner auf der Festplatte, falls er noch nicht existiert
    path.parent.mkdir(exist_ok=True)
    # Speichert das fertige Diagramm als hochauflösendes Bild (PNG) ab
    fig.savefig(path, dpi=150)

