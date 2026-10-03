from collections import Counter
import logging
import re
import unicodedata

from .base import registry
from .conf import get_setting
from .discover import autodiscover
from .exceptions import (
    LanguageCodeError,
    LanguageDetectionError,
    LanguagePackNotFound,
)

LOGGER = logging.getLogger(__file__)

__title__ = "transliterate.utils"
__author__ = "Artur Barseghyan"
__copyright__ = "2013-2017 Artur Barseghyan"
__license__ = "GPL 2.0/LGPL 2.1"
__all__ = (
    "detect_language",
    "get_available_language_codes",
    "get_available_language_packs",
    "slugify",
    "suggest",
    "translit",
)


def _(val):
    return val


def ensure_autodiscover():

    if not registry.registry:
        autodiscover()


def translit(value, language_code=None, reversed=False, strict=False):
    ensure_autodiscover()

    if language_code is None and reversed is False:
        raise LanguageCodeError(_("``language_code`` is optional with ``reversed`` set to True only."))

    if language_code is None:
        language_code = detect_language(value, fail_silently=False)

    cls = registry.get(language_code)

    if cls is None:
        raise LanguagePackNotFound(_("Language pack for code %s is not found." % language_code))

    language_pack = cls()
    return language_pack.translit(value, reversed=reversed, strict=strict)


def suggest(value, language_code=None, reversed=False, limit=None):
    ensure_autodiscover()

    if language_code is None and reversed is False:
        raise LanguageCodeError(_("``language_code`` is optional with ``reversed`` set to True only."))

    cls = registry.get(language_code)

    if cls is None:
        raise LanguagePackNotFound(_("Language pack for code %s is not found." % language_code))

    language_pack = cls()

    return language_pack.suggest(value, reversed=reversed, limit=limit)


def get_available_language_codes():
    ensure_autodiscover()

    return [key for (key, val) in registry.registry.items()]


def get_available_language_packs():
    ensure_autodiscover()

    return [val for (key, val) in registry.registry.items()]


def get_language_pack(language_code):
    ensure_autodiscover()
    return registry.registry.get(language_code, None)


def strip_numbers(text):
    return "".join(filter(lambda u: not u.isdigit(), text))


def extract_most_common_words(text, num_words=None):
    if num_words is None:
        num_words = get_setting("LANGUAGE_DETECTION_MAX_NUM_KEYWORDS")

    text = strip_numbers(text)
    counter = Counter()
    for word in text.split(" "):
        if len(word) > 1:
            counter[word] += 1
    return counter.most_common(num_words)


def detect_language(text, num_words=None, fail_silently=True, heavy_check=False):
    ensure_autodiscover()

    if num_words is None:
        num_words = get_setting("LANGUAGE_DETECTION_MAX_NUM_KEYWORDS")

    most_common_words = extract_most_common_words(text, num_words=num_words)

    counter = Counter()

    available_language_packs = get_available_language_packs()

    for word, occurrences in most_common_words:
        for letter in word:
            for language_pack in available_language_packs:
                if language_pack.detectable and language_pack.contains(letter):
                    counter[language_pack.language_code] += 1
                    continue
    try:
        return counter.most_common(1)[0][0]
    except Exception as err:
        if get_setting("DEBUG"):
            LOGGER.debug(str(err))

    if not fail_silently:
        raise LanguageDetectionError(_("""Can't detect language for the text "%s" given.""") % text)


def slugify(text, language_code=None):
    if not language_code:
        language_code = detect_language(text)
    if language_code:
        transliterated_text = translit(text, language_code, reversed=True)
        slug = unicodedata.normalize("NFKD", transliterated_text).encode("ascii", "ignore").decode("ascii")
        slug = re.sub(r"[^\w\s-]", "", slug).strip().lower()
        return re.sub(r"[-\s]+", "-", slug)
