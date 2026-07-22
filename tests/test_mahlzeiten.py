from custom_components.speiseplaner.mahlzeiten import (
    MAHLZEIT_LABELS,
    MAHLZEIT_REIHENFOLGE,
    MAHLZEITEN,
)


def test_mahlzeiten_liste_ist_nicht_leer():
    assert len(MAHLZEITEN) > 0


def test_alle_ids_sind_eindeutig():
    ids = [m["id"] for m in MAHLZEITEN]
    assert len(ids) == len(set(ids))


def test_reihenfolge_und_labels_passen_zur_liste():
    assert MAHLZEIT_REIHENFOLGE == [m["id"] for m in MAHLZEITEN]
    for m in MAHLZEITEN:
        assert MAHLZEIT_LABELS[m["id"]] == m["name"]