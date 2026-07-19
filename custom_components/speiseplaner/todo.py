from homeassistant.components.todo import (
    TodoItem,
    TodoItemStatus,
    TodoListEntity,
    TodoListEntityFeature,
)

from .const import DOMAIN
from .entity import StorageUpdateMixin, build_device_info


async def async_setup_entry(hass, entry, async_add_entities):
    storage = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([EinkaufslisteTodoListEntity(storage, entry.entry_id)])


def _format_summary(eintrag: dict) -> str:
    teile = []
    if eintrag.get("kategorie"):
        teile.append(f"{eintrag['kategorie']}: ")
    teile.append(eintrag["name"])
    if eintrag.get("einheit"):
        teile.append(f" ({eintrag['anzahl']} {eintrag['einheit']})")
    return "".join(teile)


class EinkaufslisteTodoListEntity(StorageUpdateMixin, TodoListEntity):
    _attr_name = "Speiseplaner Einkaufsliste"
    _attr_supported_features = (
        TodoListEntityFeature.CREATE_TODO_ITEM
        | TodoListEntityFeature.UPDATE_TODO_ITEM
        | TodoListEntityFeature.DELETE_TODO_ITEM
    )

    def __init__(self, storage, entry_id):
        self.storage = storage
        self._attr_unique_id = f"{entry_id}_einkaufsliste"
        self._attr_device_info = build_device_info(entry_id)

    @property
    def todo_items(self) -> list[TodoItem]:
        # Kein natives Gruppieren/Einklappen in der Standard-Todo-Karte:
        # Sortierung nach Kategorie + Präfix im Text sind die Annäherung,
        # bis dafür eine eigene Lovelace-Karte existiert.
        eintraege = sorted(
            self.storage.data["einkaufsliste"],
            key=lambda e: (e["erledigt"], e.get("kategorie", ""), e["name"]),
        )
        return [
            TodoItem(
                uid=eintrag["id"],
                summary=_format_summary(eintrag),
                status=(
                    TodoItemStatus.COMPLETED
                    if eintrag["erledigt"]
                    else TodoItemStatus.NEEDS_ACTION
                ),
            )
            for eintrag in eintraege
        ]

    async def async_create_todo_item(self, item: TodoItem) -> None:
        self.storage.add_einkaufsliste_eintrag(name=item.summary, anzahl=1, einheit="")
        await self.storage.async_save()
        self.async_write_ha_state()

    async def async_update_todo_item(self, item: TodoItem) -> None:
        # Nur der Erledigt-Status wird übernommen: da 'summary' aus
        # Kategorie/Name/Menge/Einheit zusammengesetzt ist, ließe sich ein
        # frei editierter Text nicht verlustfrei zurück in diese Felder
        # auflösen. Umbenennen/Mengenänderung laufen über die update_*-Services.
        eintrag = self.storage.find("einkaufsliste", item.uid)
        if eintrag is None:
            return
        if item.status is not None:
            eintrag["erledigt"] = item.status == TodoItemStatus.COMPLETED
        await self.storage.async_save()
        self.async_write_ha_state()

    async def async_delete_todo_items(self, uids: list[str]) -> None:
        for uid in uids:
            self.storage.remove("einkaufsliste", uid)
        await self.storage.async_save()
        self.async_write_ha_state()
