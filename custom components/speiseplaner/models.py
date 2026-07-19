from dataclasses import dataclass, asdict
from typing import List


@dataclass
class Zutat:
    name: str
    anzahl: float
    einheit: str

    def scale(self, factor: float):
        return Zutat(
            name=self.name,
            anzahl=round(self.anzahl * factor, 2),
            einheit=self.einheit,
        )


@dataclass
class Recipe:
    id: str
    name: str
    servings: int
    ingredients: List[Zutat]
    instructions: str = ""

    def scale_to(self, servings: int) -> List[Zutat]:
        factor = servings / self.servings
        return [i.scale(factor) for i in self.ingredients]


@dataclass
class MealPlanEntry:
    date: str  # YYYY-MM-DD
    recipe_id: str
    servings: int