import uuid
from homeassistant.core import HomeAssistant, ServiceCall
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

        storage.data["rezepte"].append(rezept.__dict__)
        await storage.async_save()

    async def add_speiseplaneintrag(call: ServiceCall):
        entry = Speiseplaneintrag(
            datum=call.data["datum"],
            rezept_id=call.data["rezept_id"],
            portionen=call.data["portionen"],
        )

        storage.data["speiseplan"].append(entry.__dict__)
        await storage.async_save()

    async def add_kategorie(call: ServiceCall):
        kategorie = Kategorie(
            id=str(uuid.uuid4()),
            autoeinkauf=call.data["autoeinkauf"],
            name=call.data["name"],
        )

        storage.data["kategorien"].append(kategorie.__dict__)
        await storage.async_save()

    hass.services.async_register(DOMAIN, "add_rezept", add_rezept)
    hass.services.async_register(DOMAIN, "add_speiseplaneintrag", add_speiseplaneintrag)
    hass.services.async_register(DOMAIN, "add_kategorie", add_kategorie)