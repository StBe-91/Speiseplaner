import uuid
from dataclasses import asdict
from typing import List, Optional

from homeassistant.helpers.storage import Store

from .const import STORAGE_KEY, STORAGE_VERSION
from .models import Einkaufslisteneintrag, Zutat


class SpeiseplanerStorage:
    def __init__(self, hass):
        self.store = Store(hass, STORAGE_VERSION, STORAGE_KEY)
        self.data = {"rezepte": [], "speiseplan": [], "kategorien": [], "einkaufsliste": []}

    async def async_load(self):
        stored = await self.store.async_load()
        if stored:
            self.data = stored
            self.data.setdefault("einkaufsliste", [])

    async def async_save(self):
        await self.store.async_save(self.data)

    def find(self, collection: str, id_: str) -> Optional[dict]:
        return next((item for item in self.data[collection] if item["id"] == id_), None)

    def remove(self, collection: str, id_: str) -> bool:
        item = self.find(collection, id_)
        if item is None:
            return False
        self.data[collection].remove(item)
        return True

    def get_kategorie(self, name: str) -> Optional[dict]:
        return next((k for k in self.data["kategorien"] if k["name"] == name), None)

    def add_einkaufsliste_eintrag(
        self, name: str, anzahl: float, einheit: str, kategorie: str = ""
    ) -> None:
        existing = next(
            (
                eintrag
                for eintrag in self.data["einkaufsliste"]
                if eintrag["name"] == name
                and eintrag["einheit"] == einheit
                and not eintrag["erledigt"]
            ),
            None,
        )
        if existing:
            existing["anzahl"] = round(existing["anzahl"] + anzahl, 2)
        else:
            self.data["einkaufsliste"].append(
                asdict(
                    Einkaufslisteneintrag(
                        id=str(uuid.uuid4()),
                        name=name,
                        anzahl=anzahl,
                        einheit=einheit,
                        kategorie=kategorie,
                    )
                )
            )

    def add_zutaten_to_einkaufsliste(self, zutaten: List[Zutat]) -> None:
        for zutat in zutaten:
            kategorie = self.get_kategorie(zutat.kategorie)
            if not kategorie or not kategorie["autoeinkauf"]:
                continue
            self.add_einkaufsliste_eintrag(zutat.name, zutat.anzahl, zutat.einheit, zutat.kategorie)