from dataclasses import dataclass, asdict
from typing import List


@dataclass
class Zutat:
    name: str
    anzahl: float
    einheit: str
    kategorie: str

    def scale(self, factor: float):
        return Zutat(
            name=self.name,
            anzahl=round(self.anzahl * factor, 2),
            einheit=self.einheit,
            kategorie=self.kategorie,
        )


@dataclass
class Rezept:
    id: str
    name: str
    portionen: int
    zutaten: List[Zutat]
    rezeptanleitung: str = ""
    vorbereitungsdauer: int = 0
    zubereitungsdauer: int = 0
    bild: str = ""

    def scale_to(self, portionen: int) -> List[Zutat]:
        factor = portionen / self.portionen
        return [i.scale(factor) for i in self.zutaten]


@dataclass
class Speiseplaneintrag:
    id: str
    datum: str  # YYYY-MM-DD
    rezept_id: str
    portionen: int
    mahlzeit: str = ""

@dataclass
class Kategorie:
    id: str
    name: str
    autoeinkauf: bool


@dataclass
class Einkaufslisteneintrag:
    id: str
    name: str
    anzahl: float
    einheit: str
    kategorie: str
    erledigt: bool = False