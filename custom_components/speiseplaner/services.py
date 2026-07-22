import uuid
from dataclasses import asdict

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ServiceValidationError

from .const import DOMAIN
from .models import Rezept, Zutat, Speiseplaneintrag, Kategorie


async def async_setup_services(hass: HomeAssistant, storage):

    # -- Rezepte ----------------------------------------------------------

    async def add_rezept(call: ServiceCall):
        rezept = Rezept(
            id=str(uuid.uuid4()),
            name=call.data["name"],
            portionen=call.data["portionen"],
            zutaten=[
                Zutat(**i) for i in call.data["zutaten"]
            ],
            rezeptanleitung=call.data.get("rezeptanleitung", ""),
            vorbereitungsdauer=call.data.get("vorbereitungsdauer", 0),
            zubereitungsdauer=call.data.get("zubereitungsdauer", 0),
            bild=call.data.get("bild", ""),
        )

        storage.data["rezepte"].append(asdict(rezept))
        await storage.async_save()

    async def update_rezept(call: ServiceCall):
        rezept_id = call.data["rezept_id"]
        rezept_data = storage.find("rezepte", rezept_id)
        if rezept_data is None:
            raise ServiceValidationError(f"Rezept mit ID '{rezept_id}' wurde nicht gefunden.")

        rezept = Rezept(
            id=rezept_id,
            name=call.data["name"],
            portionen=call.data["portionen"],
            zutaten=[Zutat(**i) for i in call.data["zutaten"]],
            rezeptanleitung=call.data.get("rezeptanleitung", ""),
            vorbereitungsdauer=call.data.get("vorbereitungsdauer", 0),
            zubereitungsdauer=call.data.get("zubereitungsdauer", 0),
            bild=call.data.get("bild", ""),
        )
        rezept_data.clear()
        rezept_data.update(asdict(rezept))
        await storage.async_save()

    async def delete_rezept(call: ServiceCall):
        rezept_id = call.data["rezept_id"]
        if any(entry["rezept_id"] == rezept_id for entry in storage.data["speiseplan"]):
            raise ServiceValidationError(
                f"Rezept mit ID '{rezept_id}' ist noch im Speiseplan eingeplant und kann nicht gelöscht werden."
            )
        if not storage.remove("rezepte", rezept_id):
            raise ServiceValidationError(f"Rezept mit ID '{rezept_id}' wurde nicht gefunden.")
        await storage.async_save()

    # -- Speiseplan ---------------------------------------------------------

    async def add_speiseplaneintrag(call: ServiceCall):
        rezept_id = call.data["rezept_id"]
        portionen = call.data["portionen"]

        rezept_data = storage.find("rezepte", rezept_id)
        if rezept_data is None:
            raise ServiceValidationError(
                f"Rezept mit ID '{rezept_id}' wurde nicht gefunden."
            )

        entry = Speiseplaneintrag(
            id=str(uuid.uuid4()),
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
            vorbereitungsdauer=rezept_data.get("vorbereitungsdauer", 0),
            zubereitungsdauer=rezept_data.get("zubereitungsdauer", 0),
            bild=rezept_data.get("bild", ""),
        )
        storage.add_zutaten_to_einkaufsliste(rezept.scale_to(portionen))

        await storage.async_save()

    async def update_speiseplaneintrag(call: ServiceCall):
        speiseplaneintrag_id = call.data["speiseplaneintrag_id"]
        eintrag_data = storage.find("speiseplan", speiseplaneintrag_id)
        if eintrag_data is None:
            raise ServiceValidationError(
                f"Speiseplaneintrag mit ID '{speiseplaneintrag_id}' wurde nicht gefunden."
            )

        rezept_id = call.data["rezept_id"]
        if storage.find("rezepte", rezept_id) is None:
            raise ServiceValidationError(f"Rezept mit ID '{rezept_id}' wurde nicht gefunden.")

        eintrag = Speiseplaneintrag(
            id=speiseplaneintrag_id,
            datum=call.data["datum"],
            rezept_id=rezept_id,
            portionen=call.data["portionen"],
        )
        eintrag_data.clear()
        eintrag_data.update(asdict(eintrag))
        await storage.async_save()

    async def delete_speiseplaneintrag(call: ServiceCall):
        speiseplaneintrag_id = call.data["speiseplaneintrag_id"]
        if not storage.remove("speiseplan", speiseplaneintrag_id):
            raise ServiceValidationError(
                f"Speiseplaneintrag mit ID '{speiseplaneintrag_id}' wurde nicht gefunden."
            )
        await storage.async_save()

    # -- Kategorien -----------------------------------------------------

    async def add_kategorie(call: ServiceCall):
        kategorie = Kategorie(
            id=str(uuid.uuid4()),
            autoeinkauf=call.data["autoeinkauf"],
            name=call.data["name"],
        )

        storage.data["kategorien"].append(asdict(kategorie))
        await storage.async_save()

    async def update_kategorie(call: ServiceCall):
        kategorie_id = call.data["kategorie_id"]
        kategorie_data = storage.find("kategorien", kategorie_id)
        if kategorie_data is None:
            raise ServiceValidationError(f"Kategorie mit ID '{kategorie_id}' wurde nicht gefunden.")

        kategorie = Kategorie(
            id=kategorie_id,
            name=call.data["name"],
            autoeinkauf=call.data["autoeinkauf"],
        )
        kategorie_data.clear()
        kategorie_data.update(asdict(kategorie))
        await storage.async_save()

    async def delete_kategorie(call: ServiceCall):
        kategorie_id = call.data["kategorie_id"]
        if not storage.remove("kategorien", kategorie_id):
            raise ServiceValidationError(f"Kategorie mit ID '{kategorie_id}' wurde nicht gefunden.")
        await storage.async_save()

    # -- Einkaufsliste ----------------------------------------------------

    async def add_einkaufsliste_eintrag(call: ServiceCall):
        storage.add_einkaufsliste_eintrag(
            name=call.data["name"],
            anzahl=call.data["anzahl"],
            einheit=call.data["einheit"],
            kategorie=call.data.get("kategorie", ""),
        )
        await storage.async_save()

    async def delete_einkaufsliste_eintrag(call: ServiceCall):
        einkaufslisteneintrag_id = call.data["einkaufslisteneintrag_id"]
        if not storage.remove("einkaufsliste", einkaufslisteneintrag_id):
            raise ServiceValidationError(
                f"Einkaufslisteneintrag mit ID '{einkaufslisteneintrag_id}' wurde nicht gefunden."
            )
        await storage.async_save()

    async def set_einkaufsliste_erledigt(call: ServiceCall):
        einkaufslisteneintrag_id = call.data["einkaufslisteneintrag_id"]
        eintrag_data = storage.find("einkaufsliste", einkaufslisteneintrag_id)
        if eintrag_data is None:
            raise ServiceValidationError(
                f"Einkaufslisteneintrag mit ID '{einkaufslisteneintrag_id}' wurde nicht gefunden."
            )
        eintrag_data["erledigt"] = call.data["erledigt"]
        await storage.async_save()

    hass.services.async_register(DOMAIN, "add_rezept", add_rezept)
    hass.services.async_register(DOMAIN, "update_rezept", update_rezept)
    hass.services.async_register(DOMAIN, "delete_rezept", delete_rezept)

    hass.services.async_register(DOMAIN, "add_speiseplaneintrag", add_speiseplaneintrag)
    hass.services.async_register(DOMAIN, "update_speiseplaneintrag", update_speiseplaneintrag)
    hass.services.async_register(DOMAIN, "delete_speiseplaneintrag", delete_speiseplaneintrag)

    hass.services.async_register(DOMAIN, "add_kategorie", add_kategorie)
    hass.services.async_register(DOMAIN, "update_kategorie", update_kategorie)
    hass.services.async_register(DOMAIN, "delete_kategorie", delete_kategorie)

    hass.services.async_register(DOMAIN, "add_einkaufsliste_eintrag", add_einkaufsliste_eintrag)
    hass.services.async_register(DOMAIN, "delete_einkaufsliste_eintrag", delete_einkaufsliste_eintrag)
    hass.services.async_register(DOMAIN, "set_einkaufsliste_erledigt", set_einkaufsliste_erledigt)
