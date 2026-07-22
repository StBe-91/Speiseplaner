"""Feste Mahlzeiten-Typen für den Speiseplan.

Anders als bei den Kategorien ist diese Liste bewusst nicht über die UI
erweiterbar - falls doch mal eine weitere Mahlzeit gebraucht wird, reicht
ein zusätzlicher Eintrag hier.
"""

MAHLZEITEN = [
    {"id": "fruehstueck", "name": "Frühstück"},
    {"id": "mittagessen", "name": "Mittagessen"},
    {"id": "vesper", "name": "Vesper"},
    {"id": "abendbrot", "name": "Abendbrot"},
]

MAHLZEIT_REIHENFOLGE = [m["id"] for m in MAHLZEITEN]
MAHLZEIT_LABELS = {m["id"]: m["name"] for m in MAHLZEITEN}