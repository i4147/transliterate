__title__ = "transliterate.exceptions"
__author__ = "Artur Barseghyan"
__copyright__ = "2013-2017 Artur Barseghyan"
__license__ = "GPL 2.0/LGPL 2.1"
__all__ = (
    "ImproperlyConfigured",
    "InvalidRegistryItemType",
    "LanguageCodeError",
    "LanguageDetectionError",
    "LanguagePackNotFound",
)


class LanguageCodeError(Exception):
    pass


class ImproperlyConfigured(Exception):
    pass


class LanguagePackNotFound(Exception):
    pass


class LanguageDetectionError(Exception):
    pass


class InvalidRegistryItemType(ValueError):
    pass
