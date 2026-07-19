from homeassistant.components.todo import TodoItem, TodoItemStatus

from custom_components.speiseplaner.storage import SpeiseplanerStorage
from custom_components.speiseplaner.todo import EinkaufslisteTodoListEntity


def make_storage():
    return SpeiseplanerStorage(hass=object())


def test_todo_items_zeigt_kategorie_als_praefix():
    storage = make_storage()
    storage.add_einkaufsliste_eintrag("Hackfleisch", 500, "g", "Fleisch")
    entity = EinkaufslisteTodoListEntity(storage, "entry1")

    items = entity.todo_items

    assert items[0].summary == "Fleisch: Hackfleisch (500 g)"


def test_todo_items_ohne_kategorie_und_einheit():
    storage = make_storage()
    storage.add_einkaufsliste_eintrag("Milch", 1, "")
    entity = EinkaufslisteTodoListEntity(storage, "entry1")

    assert entity.todo_items[0].summary == "Milch"


def test_todo_items_sortiert_offene_vor_erledigten_und_nach_kategorie():
    storage = make_storage()
    storage.add_einkaufsliste_eintrag("Zwiebeln", 2, "Stk", "Gemüse")
    storage.add_einkaufsliste_eintrag("Hackfleisch", 500, "g", "Fleisch")
    storage.data["einkaufsliste"][0]["erledigt"] = True  # Zwiebeln erledigt
    entity = EinkaufslisteTodoListEntity(storage, "entry1")

    namen = [item.summary for item in entity.todo_items]

    assert namen == ["Fleisch: Hackfleisch (500 g)", "Gemüse: Zwiebeln (2 Stk)"]


def test_todo_items_setzt_status_korrekt():
    storage = make_storage()
    storage.add_einkaufsliste_eintrag("Milch", 1, "l")
    storage.data["einkaufsliste"][0]["erledigt"] = True
    entity = EinkaufslisteTodoListEntity(storage, "entry1")

    assert entity.todo_items[0].status == TodoItemStatus.COMPLETED


async def test_async_create_todo_item_legt_freitext_eintrag_an():
    storage = make_storage()
    entity = EinkaufslisteTodoListEntity(storage, "entry1")

    await entity.async_create_todo_item(TodoItem(summary="Klopapier"))

    assert len(storage.data["einkaufsliste"]) == 1
    assert storage.data["einkaufsliste"][0]["name"] == "Klopapier"
    assert storage.data["einkaufsliste"][0]["erledigt"] is False


async def test_async_update_todo_item_setzt_erledigt():
    storage = make_storage()
    storage.add_einkaufsliste_eintrag("Milch", 1, "l")
    eintrag_id = storage.data["einkaufsliste"][0]["id"]
    entity = EinkaufslisteTodoListEntity(storage, "entry1")

    await entity.async_update_todo_item(TodoItem(uid=eintrag_id, status=TodoItemStatus.COMPLETED))

    assert storage.data["einkaufsliste"][0]["erledigt"] is True


async def test_async_update_todo_item_ignoriert_unbekannte_id():
    storage = make_storage()
    entity = EinkaufslisteTodoListEntity(storage, "entry1")

    await entity.async_update_todo_item(TodoItem(uid="unbekannt", status=TodoItemStatus.COMPLETED))

    assert storage.data["einkaufsliste"] == []


async def test_async_delete_todo_items_entfernt_mehrere():
    storage = make_storage()
    storage.add_einkaufsliste_eintrag("Milch", 1, "l")
    storage.add_einkaufsliste_eintrag("Butter", 1, "Stk")
    uids = [e["id"] for e in storage.data["einkaufsliste"]]
    entity = EinkaufslisteTodoListEntity(storage, "entry1")

    await entity.async_delete_todo_items(uids)

    assert storage.data["einkaufsliste"] == []
