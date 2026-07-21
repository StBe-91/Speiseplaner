from custom_components.speiseplaner.kategorien_defaults import DEFAULT_KATEGORIEN


def test_kategorien_liste_ist_nicht_leer():
    assert len(DEFAULT_KATEGORIEN) > 0


def test_alle_ids_sind_eindeutig():
    ids = [k["id"] for k in DEFAULT_KATEGORIEN]
    assert len(ids) == len(set(ids))


def test_alle_kategorien_haben_name_und_autoeinkauf():
    for kategorie in DEFAULT_KATEGORIEN:
        assert kategorie["name"]
        assert isinstance(kategorie["autoeinkauf"], bool)
