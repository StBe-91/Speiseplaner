import uuid
from dataclasses import asdict

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ServiceValidationError

from .const import DOMAIN
from .models import Rezept, Zutat, Speiseplaneintrag, Kategorie


async def async_setup_services(hass: HomeAssistant, storage):

    async def add_rezept(call: ServiceCall):
        rezept = Rezept(
            id=str(uuid.uuid4()),
            name=call.data["name"],
            portionen=call.data["portionen"],
            zutaten=[
                Zutat(**i) for i in call.data["zutaten"]
            ],
            rezeptanleitung=call.data.get("rezeptanleitung", ""),
        )

        storage.data["rezepte"].append(asdict(rezept))
        await storage.async_save()

    async def add_speiseplaneintrag(call: ServiceCall):
        rezept_id = call.data["rezept_id"]
        portionen = call.data["portionen"]

        rezept_data = next(
            (r for r in storage.data["rezepte"] if r["id"] == rezept_id), None
        )
        if rezept_data is None:
            raise ServiceValidationError(
                f"Rezept mit ID '{rezept_id}' wurde nicht gefunden."
            )

        entry = Speiseplaneintrag(
            datum=call.data["datum"],
            rezept_id=rezept_id,
            portionen=portionen,
        )
        storage.data["speiseplan"].append(asdict(entry))

        rezept = Rezept(
            id=rezept_data["id"],
            name=rezept_data["name"],
            portionen=rezept_data["portionen"],
            zutaten=[Zutat(**z) for z in rezept_data["zutaten"]],
            rezeptanleitung=rezept_data.get("rezeptanleitung", ""),
        )
        storage.add_zutaten_to_einkaufsliste(rezept.scale_to(portionen))

        await storage.async_save()

    async def add_kategorie(call: ServiceCall):
        kategorie = Kategorie(
            id=str(uuid.uuid4()),
            autoeinkauf=call.data["autoeinkauf"],
            name=call.data["name"],
        )

        storage.data["kategorien"].append(asdict(kategorie))
        await storage.async_save()

    hass.services.async_register(DOMAIN, "add_rezept", add_rezept)
    hass.services.async_register(DOMAIN, "add_speiseplaneintrag", add_speiseplaneintrag)
    hass.services.async_register(DOMAIN, "add_kategorie", add_kategorie)