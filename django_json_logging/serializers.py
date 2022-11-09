import json
from typing import Callable
from functools import partial, lru_cache

from django_json_logging import settings

try:
    import ujson
except ImportError:  # pragma: nocover
    ujson = None  # type: ignore

try:
    import orjson

    options = {
        "LOGGING_OPT_INDENT_2": orjson.OPT_INDENT_2,
        "LOGGING_OPT_NON_STR_KEYS": orjson.OPT_NON_STR_KEYS,
        "LOGGING_OPT_APPEND_NEWLINE": orjson.OPT_APPEND_NEWLINE,
        "LOGGING_OPT_NAIVE_UTC": orjson.OPT_NAIVE_UTC,
        "LOGGING_OPT_OMIT_MICROSECONDS": orjson.OPT_OMIT_MICROSECONDS,
        "LOGGING_OPT_PASSTHROUGH_DATACLASS": orjson.OPT_PASSTHROUGH_DATACLASS,
        "LOGGING_OPT_PASSTHROUGH_DATETIME": orjson.OPT_PASSTHROUGH_DATETIME,
        "LOGGING_OPT_SERIALIZE_DATACLASS": orjson.OPT_SERIALIZE_DATACLASS,
        "LOGGING_OPT_SERIALIZE_NUMPY": orjson.OPT_SERIALIZE_NUMPY,
        "LOGGING_OPT_SERIALIZE_UUID": orjson.OPT_SERIALIZE_UUID,
        "LOGGING_OPT_SORT_KEYS": orjson.OPT_SORT_KEYS,
        "LOGGING_OPT_STRICT_INTEGER": orjson.OPT_STRICT_INTEGER,
        "LOGGING_OPT_UTC_Z": orjson.OPT_UTC_Z
    }

except (ImportError, AttributeError):  # pragma: nocover
    orjson = None  # type: ignore


class ORJsonSerializer:

    @staticmethod
    @lru_cache()
    def dumps() -> Callable:
        option = False
        for key, val in options.items():
            if getattr(settings, key):
                option = option | options[key]
        return partial(orjson.dumps, option=option) if option else orjson.dumps

    @classmethod
    def to_json(cls, dict_record: dict) -> str:
        """Converts record dict to a JSON string.

        The library orjson returns a bytes not an str.
        """
        assert orjson is not None, 'orjson must be installed to use ORJsonSerializer'

        return str(cls.dumps()(dict_record), settings.LOGGING_ENCODING)


class UJsonSerializer:
    @staticmethod
    def to_json(dict_record: dict) -> str:
        """Converts record dict to a JSON string.

        The library ujson returns a bytes not an str.
        """
        assert ujson is not None, 'ujson must be installed to use UJsonSerializer'

        if settings.DEVELOP:
            json = ujson.dumps(dict_record, ensure_ascii=False, indent=2)
        else:
            json = ujson.dumps(dict_record, ensure_ascii=False)
        return str(json, settings.LOGGING_ENCODING)


class JsonSerializer:
    @staticmethod
    def to_json(dict_record: dict) -> str:
        """Converts record dict to a JSON string.

        Using standard json library.
        """

        if settings.DEVELOP:
            return json.dumps(dict_record, ensure_ascii=False, indent=2)
        else:
            return json.dumps(dict_record, ensure_ascii=False)


def get_serializer():
    mapping = {
        'orjson': ORJsonSerializer,
        'ujson': UJsonSerializer,
        'json': JsonSerializer,
    }
    assert settings.LOGGING_SERIALIZER in mapping, 'LOGGING_SERIALIZER must be "orjson", "ujson" or "json"'
    return mapping[settings.LOGGING_SERIALIZER]
