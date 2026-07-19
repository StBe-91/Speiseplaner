from custom_components.speiseplaner.models import Zutat
from custom_components.speiseplaner.storage import SpeiseplanerStorage


def make_storage():
    storage = SpeiseplanerStorage(hass=object())
    storage.data["kategorien"] = [
        {"id": "k1", "name": "Fleisch", "autoeinkauf": True},
        {"id": "k2", "name": "Gewürze", "autoeinkauf": False},
    ]
    return storage


def test_get_kategorie_findet_vorhandene_kategorie():
    storage = make_storage()
    assert storage.get_kategorie("Fleisch")["id"] == "k1"


def test_get_kategorie_gibt_none_bei_unbekannter_kategorie():
    storage = make_storage()
    assert storage.get_kategorie("Unbekannt") is None


def test_zutat_mit_autoeinkauf_wird_zur_einkaufsliste_hinzugefuegt():
    storage = make_storage()
    storage.add_zutaten_to_einkaufsliste([Zutat("Hackfleisch", 500, "g", "Fleisch")])

    assert len(storage.data["einkaufsliste"]) == 1
    eintrag = storage.data["einkaufsliste"][0]
    assert eintrag["name"] == "Hackfleisch"
    assert eintrag["anzahl"] == 500
    assert eintrag["einheit"] == "g"
    assert eintrag["erledigt"] is False


def test_zutat_ohne_autoeinkauf_wird_uebersprungen():
    storage = make_storage()
    storage.add_zutaten_to_einkaufsliste([Zutat("Pfeffer", 1, "TL", "Gewürze")])

    assert storage.data["einkaufsliste"] == []


def test_zutat_mit_unbekannter_kategorie_wird_uebersprungen():
    storage = make_storage()
    storage.add_zutaten_to_einkaufsliste([Zutat("Mystery", 1, "Stk", "Nicht Vorhanden")])

    assert storage.data["einkaufsliste"] == []


def test_gleiche_zutat_wird_gemergt_statt_dupliziert():
    storage = make_storage()
    storage.add_zutaten_to_einkaufsliste([Zutat("Hackfleisch", 500, "g", "Fleisch")])
    storage.add_zutaten_to_einkaufsliste([Zutat("Hackfleisch", 250, "g", "Fleisch")])

    assert len(storage.data["einkaufsliste"]) == 1
    assert storage.data["einkaufsliste"][0]["anzahl"] == 750


def test_unterschiedliche_einheit_wird_nicht_gemergt():
    storage = make_storage()
    storage.add_zutaten_to_einkaufsliste([Zutat("Milch", 200, "ml", "Fleisch")])
    storage.add_zutaten_to_einkaufsliste([Zutat("Milch", 1, "l", "Fleisch")])

    assert len(storage.data["einkaufsliste"]) == 2


def test_find_gibt_passendes_element_zurueck():
    storage = make_storage()
    assert storage.find("kategorien", "k1")["name"] == "Fleisch"


def test_find_gibt_none_bei_unbekannter_id_zurueck():
    storage = make_storage()
    assert storage.find("kategorien", "unbekannt") is None


def test_remove_entfernt_element_und_gibt_true_zurueck():
    storage = make_storage()
    assert storage.remove("kategorien", "k1") is True
    assert storage.find("kategorien", "k1") is None


def test_remove_gibt_false_bei_unbekannter_id_zurueck():
    storage = make_storage()
    assert storage.remove("kategorien", "unbekannt") is False
    assert len(storage.data["kategorien"]) == 2


def test_manuelles_hinzufuegen_ignoriert_autoeinkauf():
    storage = make_storage()
    storage.add_einkaufsliste_eintrag("Pfeffer", 1, "TL", "Gewürze")

    assert len(storage.data["einkaufsliste"]) == 1
    assert storage.data["einkaufsliste"][0]["name"] == "Pfeffer"


def test_erledigter_eintrag_wird_nicht_wieder_aufgefuellt():
    storage = make_storage()
    storage.add_zutaten_to_einkaufsliste([Zutat("Butter", 250, "g", "Fleisch")])
    storage.data["einkaufsliste"][0]["erledigt"] = True

    storage.add_zutaten_to_einkaufsliste([Zutat("Butter", 100, "g", "Fleisch")])

    assert len(storage.data["einkaufsliste"]) == 2
    assert storage.data["einkaufsliste"][0]["erledigt"] is True
    assert storage.data["einkaufsliste"][1]["erledigt"] is False
    assert storage.data["einkaufsliste"][1]["anzahl"] == 100
