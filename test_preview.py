"""
Schnelltest-Skript: generiert einen 15-sekündigen Ausschnitt zur Validierung von Audiosynthese,
Untertitelblasen-Position, Equalizer und visuellem Rendering.
"""
import sys, os
from auto_pipeline import run_auto_pipeline

if __name__ == "__main__":
    print("[TEST] Starte 15-Sekunden-Vorschautest...")
    run_auto_pipeline(
        target_minutes=0.5,
        topic="Die Kunst des Zuhörens in der Partnerschaft",
        dry_run=True,
        preview_seconds=15.0
    )
