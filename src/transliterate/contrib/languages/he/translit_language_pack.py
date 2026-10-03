from transliterate.base import TranslitLanguagePack, registry

__title__ = "transliterate.contrib.languages.he.translit_language_pack"
__author__ = "Artur Barseghyan"
__copyright__ = "2013-2017 Artur Barseghyan"
__license__ = "GPL 2.0/LGPL 2.1"
__all__ = ("HebrewLanguagePack",)


class HebrewLanguagePack(TranslitLanguagePack):
    language_code = "he"
    language_name = "Hebrew"
    character_ranges = ((0x0530, 0x058F), (0xFB10, 0xFB1F))
    mapping = (
        "abgdvzhilmnsfckrt",
        # trkcfsnmlihzvdgbа
        "אבגדוזחילמנספצקרת",
    )
    reversed_specific_mapping = (
        "פ",
        # p
        "p",
    )
    pre_processor_mapping = {
        # lowercase
        "ha'": "ה",
        "tt": "ט",
        "ka": "כ",
        "aa": "ע",
        "sh": "ש",
        "fs": "ף",
        "cs": "ץ",
        "ms": "ם",
        "ns": "ן",
        "ks": "ך",
    }
    detectable = True


# registry.register(HebrewLanguagePack)
