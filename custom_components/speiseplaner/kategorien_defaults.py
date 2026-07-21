"""Standard-Kategorien, die bei der Einrichtung zur Auswahl angeboten werden.

Neue Kategorie ergänzen: einfach einen weiteren Eintrag mit eindeutiger
'id' (Kleinbuchstaben, keine Leerzeichen), einem Namen im Format
'{Emoji} {Name}' und autoeinkauf hinzufügen. Mehr Vorwissen braucht es
dafür nicht - der Rest (Auswahlformular, Speicherung) läuft automatisch mit.
"""

DEFAULT_KATEGORIEN = [
    {"id": "obst_gemuese", "name": "🥦 Obst & Gemüse", "autoeinkauf": True},
    {"id": "brot_backwaren", "name": "🍞 Brot & Backwaren", "autoeinkauf": True},
    {"id": "milchprodukte_kaese", "name": "🥛 Milchprodukte & Käse", "autoeinkauf": True},
    {"id": "fleisch_wurst", "name": "🥩 Fleisch & Wurst", "autoeinkauf": True},
    {"id": "fisch_meeresfruechte", "name": "🐟 Fisch & Meeresfrüchte", "autoeinkauf": True},
    {"id": "tiefkuehlkost", "name": "🧊 Tiefkühlkost", "autoeinkauf": True},
    {"id": "konserven_fertiggerichte", "name": "🥫 Konserven & Fertiggerichte", "autoeinkauf": True},
    {"id": "nudeln_reis_getreide", "name": "🍝 Nudeln, Reis & Getreide", "autoeinkauf": True},
    {"id": "fruehstueck_muesli", "name": "🥣 Frühstück & Müsli", "autoeinkauf": True},
    {"id": "gewuerze_oele_saucen", "name": "🧂 Gewürze, Öle & Saucen", "autoeinkauf": True},
    {"id": "suessigkeiten_snacks", "name": "🍫 Süßigkeiten & Snacks", "autoeinkauf": True},
    {"id": "getraenke", "name": "🥤 Getränke", "autoeinkauf": True},
    {"id": "wein_bier_spirituosen", "name": "🍷 Wein, Bier & Spirituosen", "autoeinkauf": True},
    {"id": "backzutaten", "name": "🧁 Backzutaten", "autoeinkauf": True},
    {"id": "drogerie_koerperpflege", "name": "🧴 Drogerie & Körperpflege", "autoeinkauf": True},
    {"id": "haushalt_reinigung", "name": "🧽 Haushalt & Reinigung", "autoeinkauf": True},
    {"id": "baby_kind", "name": "🍼 Baby & Kind", "autoeinkauf": True},
    {"id": "tierbedarf", "name": "🐾 Tierbedarf", "autoeinkauf": True},
]
