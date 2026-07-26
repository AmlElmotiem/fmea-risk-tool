"""Core FMEA (Failure Mode and Effects Analysis) data model.

Each FailureMode represents one way a component or function can fail.
Severity, occurrence, and detection are rated 1-10 (10 = worst), per
standard FMEA practice. Their product is the Risk Priority Number
(RPN), used to prioritize which failure modes need action first.
"""

# Erlaubt es, Klassen-Typen zu nutzen, bevor sie im Code definiert sind
from __future__ import annotations

# Importiert 'dataclass' für einfache Datenspeicher und 'field' für Listen-Standards
from dataclasses import dataclass, field


@dataclass
class FailureMode:
    """
    Diese Klasse repräsentiert eine einzelne Zeile in der FMEA-Tabelle.
    Sie speichert alle Daten zu einem bestimmten Fehler an einem Bauteil.
    """
    component: str           # Name des Bauteils (z.B. "Kolbendichtung")
    function: str            # Was das Bauteil tun soll (z.B. "Druck halten")
    failure_mode: str        # Wie es kaputtgehen kann (z.B. "Dichtungsriss")
    effect: str              # Was die Auswirkung ist (z.B. "Kraftverlust")
    severity: int            # S = Schweregrad des Fehlers (Skala 1-10)
    occurrence: int          # A = Auftretenswahrscheinlichkeit (Skala 1-10)
    detection: int           # E = Entdeckungswahrscheinlichkeit (Skala 1-10)
    recommended_action: str = ""  # Empfohlene Maßnahme zur Risikosenkung (Text)

    def __post_init__(self) -> None:
        """
        GRENZWERT-VALIDIERUNG: Diese Funktion läuft automatisch direkt nach 
        dem Erstellen des Objekts. Sie schützt das System vor falschen Eingaben.
        """
        # Eine Schleife, die überprüft, ob S, A und E wirklich im erlaubten Bereich liegen
        for name, value in [
            ("severity", self.severity),
            ("occurrence", self.occurrence),
            ("detection", self.detection),
        ]:
            # Wenn ein Wert kleiner als 1 oder größer als 10 ist, bricht das Programm ab
            if not (1 <= value <= 10):
                # Das ist ein Sicherheits-Stopp (Fehlermeldung) für falsche Zahlen
                raise ValueError(f"{name} must be between 1 and 10, got {value}")

    @property
    def rpn(self) -> int:
        """
        DYNAMISCHE BERECHNUNG: Berechnet live die Risikoprioritätszahl (RPN).
        Formel: Schweregrad x Auftreten x Entdeckung (Bereich von 1 bis 1000).
        Weil hier '@property' steht, rechnet Python den Wert jedes Mal neu aus,
        wenn man 'mode.rpn' aufruft.
        """
        return self.severity * self.occurrence * self.detection

    @property
    def risk_level(self) -> str:
        """
        AUTOMATISCHE EINSTUFUNG (Risk Banding):
        Liest die berechnete RPN aus und vergibt automatisch eine Gefahrenklasse.
        """
        if self.rpn >= 200:
            return "CRITICAL"  # RPN ab 200 ist extrem gefährlich (Kritisch)
        if self.rpn >= 100:
            return "HIGH"      # RPN ab 100 ist hoch
        if self.rpn >= 40:
            return "MEDIUM"    # RPN ab 40 ist mittel
        return "LOW"           # Alles darunter ist niedrig


@dataclass
class FMEAAnalysis:
    """
    Diese Klasse ist der 'Container' (die Mappe), der alle einzelnen 
    Fehlermöglichkeiten für das gesamte Medizinprodukt sammelt.
    """
    title: str  # Der Titel des Projekts (z.B. "FMEA Pneumatikzylinder")
    # Eine Liste, in der alle 'FailureMode'-Objekte gespeichert werden
    # 'field(default_factory=list)' erstellt im Hintergrund eine leere Liste []
    failure_modes: list[FailureMode] = field(default_factory=list)

    def add(self, failure_mode: FailureMode) -> None:
        """Fügt einen neuen Fehler zur Liste hinzu."""
        self.failure_modes.append(failure_mode)

    def ranked(self) -> list[FailureMode]:
        """
        AUTOMATISCHE SORTIERUNG: Sortiert alle Fehler so, dass das größte Risiko
        (die höchste RPN) ganz oben steht.
        Genau so würde ein echtes FMEA-Meeting in der Industrie ablaufen,
        damit man die schlimmsten Fehler zuerst bespricht.
        """
        # 'key=lambda fm: fm.rpn' sagt Python: Sortiere nach dem Wert 'rpn'
        # 'reverse=True' sorgt dafür, dass es absteigend (groß nach klein) sortiert wird
        return sorted(self.failure_modes, key=lambda fm: fm.rpn, reverse=True)

    def above_threshold(self, rpn_threshold: int = 100) -> list[FailureMode]:
        """
        RISIKO-FILTER (Schwellenwert):
        Filtert alle Fehler heraus, die sofortige Maßnahmen erfordern.
        Standardmäßig werden alle Fehler angezeigt, deren RPN größer oder gleich 100 ist.
        Nutzt die elegante Python-Schreibweise 'List Comprehension'.
        """
        return [fm for fm in self.ranked() if fm.rpn >= rpn_threshold]
