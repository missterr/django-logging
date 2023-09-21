import json
from functools import partial, lru_cache
from typing import Callable

from django_json_logging import settings

try:
    import ujson
except ImportError:  # pragma: nocover
    ujson = None  # type: ignore

try:
    import orjson
except (ImportError, AttributeError):  # pragma: nocover
    orjson = None  # type: ignore


options = {
    "LOGGING_OPT_INDENT_2": "OPT_INDENT_2",
    "LOGGING_OPT_NON_STR_KEYS": "OPT_NON_STR_KEYS",
    "LOGGING_OPT_APPEND_NEWLINE": "OPT_APPEND_NEWLINE",
    "LOGGING_OPT_NAIVE_UTC": "OPT_NAIVE_UTC",
    "LOGGING_OPT_OMIT_MICROSECONDS": "OPT_OMIT_MICROSECONDS",
    "LOGGING_OPT_PASSTHROUGH_DATACLASS": "OPT_PASSTHROUGH_DATACLASS",
    "LOGGING_OPT_PASSTHROUGH_DATETIME": "OPT_PASSTHROUGH_DATETIME",
    "LOGGING_OPT_SERIALIZE_DATACLASS": "OPT_SERIALIZE_DATACLASS",
    "LOGGING_OPT_SERIALIZE_NUMPY": "OPT_SERIALIZE_NUMPY",
    "LOGGING_OPT_SERIALIZE_UUID": "OPT_SERIALIZE_UUID",
    "LOGGING_OPT_SORT_KEYS": "OPT_SORT_KEYS",
    "LOGGING_OPT_STRICT_INTEGER": "OPT_STRICT_INTEGER",
    "LOGGING_OPT_UTC_Z": "OPT_UTC_Z"
}


class ORJsonSerializer:

    @staticmethod
    @lru_cache()
    def dumps() -> Callable:
        option = False
        for key, opt in options.items():
            if getattr(settings, key):
                option = option | getattr(orjson, opt)
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
            return ujson.dumps(dict_record, ensure_ascii=False, indent=2)
        else:
            return ujson.dumps(dict_record, ensure_ascii=False)


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
