from datetime import date

from custom_components.speiseplaner.sensor import SpeiseplanHeuteSensor
from custom_components.speiseplaner.storage import SpeiseplanerStorage


def make_storage():
    storage = SpeiseplanerStorage(hass=object())
    storage.data["rezepte"] = [{"id": "r1", "name": "Lasagne", "portionen": 4, "zutaten": [], "rezeptanleitung": ""}]
    return storage


def test_ohne_heutigen_eintrag_zeigt_kein_eintrag():
    storage = make_storage()
    sensor = SpeiseplanHeuteSensor(storage, "entry1")

    assert sensor.native_value == "Kein Eintrag"
    assert sensor.extra_state_attributes == {"anzahl_eintraege": 0}


def test_mit_heutigem_eintrag_zeigt_rezeptnamen():
    storage = make_storage()
    heute = date.today().isoformat()
    storage.data["speiseplan"] = [{"id": "s1", "datum": heute, "rezept_id": "r1", "portionen": 4}]
    sensor = SpeiseplanHeuteSensor(storage, "entry1")

    assert sensor.native_value == "Lasagne"
    assert sensor.extra_state_attributes == {"anzahl_eintraege": 1}


def test_mehrere_heutige_eintraege_werden_zusammengefasst():
    storage = make_storage()
    storage.data["rezepte"].append(
        {"id": "r2", "name": "Salat", "portionen": 2, "zutaten": [], "rezeptanleitung": ""}
    )
    heute = date.today().isoformat()
    storage.data["speiseplan"] = [
        {"id": "s1", "datum": heute, "rezept_id": "r1", "portionen": 4},
        {"id": "s2", "datum": heute, "rezept_id": "r2", "portionen": 2},
    ]
    sensor = SpeiseplanHeuteSensor(storage, "entry1")

    assert sensor.native_value == "Lasagne, Salat"
    assert sensor.extra_state_attributes == {"anzahl_eintraege": 2}


def test_unbekanntes_rezept_wird_als_solches_angezeigt():
    storage = make_storage()
    heute = date.today().isoformat()
    storage.data["speiseplan"] = [{"id": "s1", "datum": heute, "rezept_id": "unbekannt", "portionen": 4}]
    sensor = SpeiseplanHeuteSensor(storage, "entry1")

    assert sensor.native_value == "Unbekanntes Rezept"


def test_eintrag_an_anderem_tag_wird_ignoriert():
    storage = make_storage()
    storage.data["speiseplan"] = [{"id": "s1", "datum": "2000-01-01", "rezept_id": "r1", "portionen": 4}]
    sensor = SpeiseplanHeuteSensor(storage, "entry1")

    assert sensor.native_value == "Kein Eintrag"
