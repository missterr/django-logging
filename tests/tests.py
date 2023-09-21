import json
import logging
from io import StringIO
from unittest import TestCase

from django_json_logging import settings
from django_json_logging.formatters import JSONFormatter

stream = StringIO()


class JsonFormatterTestCase(TestCase):
    def setUp(self) -> None:
        self.logger = logging.getLogger('test-json-logger')
        handler = logging.StreamHandler(stream=stream)
        handler.setFormatter(JSONFormatter())
        self.logger.addHandler(handler)

    def test_write(self):
        """Common writing with the extra fields"""
        self.logger.error('Something bad happened', extra={'error_code': 'xxx'})
        result = json.loads(stream.getvalue())
        for key in settings.LOGGING_FIELDS:
            self.assertIn(key, result.keys())

        self.assertIn('error_code', result.keys())
        self.assertEqual(result['error_code'], 'xxx')
