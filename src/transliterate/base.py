import re
import unicodedata

import six

from .exceptions import ImproperlyConfigured, InvalidRegistryItemType

__title__ = "transliterate.base"
__author__ = "Artur Barseghyan"
__copyright__ = "2013-2017 Artur Barseghyan"
__license__ = "GPL 2.0/LGPL 2.1"
__all__ = (
    "registry",
    "TranslitLanguagePack",
)


class TranslitLanguagePack(object):
    language_code = None
    language_name = None
    character_ranges = None
    mapping = None
    reversed_specific_mapping = None

    reversed_pre_processor_mapping_keys = []

    reversed_specific_pre_processor_mapping = None
    reversed_specific_pre_processor_mapping_keys = []

    pre_processor_mapping = None
    pre_processor_mapping_keys = []

    detectable = False
    characters = None
    reversed_characters = None

    def __init__(self):
        try:
            assert self.language_code is not None
            assert self.language_name is not None
            assert self.mapping
        except AssertionError:
            raise ImproperlyConfigured(
                "You should define ``language_code``, ``language_name`` and "
                "``mapping`` properties in your subclassed "
                "``TranslitLanguagePack`` class."
            )

        super(TranslitLanguagePack, self).__init__()

        self.translation_table = {}

        for key, val in zip(*self.mapping):
            self.translation_table.update({ord(key): ord(val)})

        self.reversed_translation_table = dict(zip(self.translation_table.values(), self.translation_table.keys()))

        if self.pre_processor_mapping:
            self.reversed_pre_processor_mapping = dict(
                zip(self.pre_processor_mapping.values(), self.pre_processor_mapping.keys())
            )
            self.pre_processor_mapping_keys = self.pre_processor_mapping.keys()
            self.reversed_pre_processor_mapping_keys = self.pre_processor_mapping.values()

        else:
            self.reversed_pre_processor_mapping = None

        if self.reversed_specific_mapping:
            self.reversed_specific_translation_table = {}
            for key, val in zip(*self.reversed_specific_mapping):
                self.reversed_specific_translation_table.update({ord(key): ord(val)})

        if self.reversed_specific_pre_processor_mapping:
            self.reversed_specific_pre_processor_mapping_keys = self.reversed_specific_pre_processor_mapping.keys()

        self._characters = "[^]"

        if self.characters is not None:
            self._characters = "[^{0}]".format("\\".join(list(self.characters)))

        self._reversed_characters = "[^]"
        if self.reversed_characters is not None:
            self._reversed_characters = "[^{0}]".format("\\".join(list(self.characters)))

    def translit(self, value, reversed=False, strict=False, fail_silently=True):
        if not six.PY3:
            value = unicode(value)

        if reversed:
            if self.reversed_specific_mapping:
                value = value.translate(self.reversed_specific_translation_table)

            if self.reversed_specific_pre_processor_mapping:
                for rule in self.reversed_specific_pre_processor_mapping_keys:
                    value = value.replace(rule, self.reversed_specific_pre_processor_mapping[rule])

            if self.reversed_pre_processor_mapping:
                for rule in self.reversed_pre_processor_mapping_keys:
                    value = value.replace(rule, self.reversed_pre_processor_mapping[rule])

            return value.translate(self.reversed_translation_table)

        if self.pre_processor_mapping:
            for rule in self.pre_processor_mapping_keys:
                value = value.replace(rule, self.pre_processor_mapping[rule])
        res = value.translate(self.translation_table)

        if strict:
            res = self._make_strict(value=res, reversed=reversed, fail_silently=fail_silently)

        return res

    def _make_strict(self, value, reversed=False, fail_silently=True):
        try:
            return self.make_strict(value, reversed)
        except Exception as err:
            if fail_silently:
                return value
            else:
                raise err

    def make_strict(self, value, reversed=False):
        if reversed:
            if self.reversed_characters:
                value = re.sub(self._reversed_characters, "", value)
            else:
                pass
        else:
            if self.characters:
                value = re.sub(self._characters, "", value)
            else:
                pass

        return value

    @classmethod
    def contains(cls, character):
        if cls.character_ranges:
            char_num = unicodedata.normalize("NFC", character)
            char_num = ord(char_num)
            for character_range in cls.character_ranges:
                range_lower = character_range[0]
                range_upper = character_range[1]
                if char_num >= range_lower and char_num <= range_upper:
                    return True
        return False

    @classmethod
    def suggest(value, reversed=False, limit=None):
        pass
        # TODO

    @classmethod
    def detect(text, num_words=None):
        pass
        # TODO


class TranslitRegistry(object):
    def __init__(self):
        self._registry = {}
        self._forced = []

    @property
    def registry(self):
        return self._registry

    def register(self, cls, force=False):
        if not issubclass(cls, TranslitLanguagePack):
            raise InvalidRegistryItemType("Invalid item type `%s` for registry `%s`", cls, self.__class__)

        if force:
            if cls.language_code not in self._forced:
                self._registry[cls.language_code] = cls
                self._forced.append(cls.language_code)
                return True
            else:
                return False

        else:
            if cls.language_code in self._registry:
                return False
            else:
                self._registry[cls.language_code] = cls
                return True

    def unregister(self, cls):
        if not issubclass(cls, TranslitLanguagePack):
            raise InvalidRegistryItemType("Invalid item type `%s` for registry `%s`", cls, self.__class__)

        if cls.language_code in self._registry and cls.language_code not in self._forced:
            self._registry.pop(cls.language_code)
            return True
        else:
            return False

    def get(self, language_code, default=None):
        return self._registry.get(language_code, default)


registry = TranslitRegistry()
