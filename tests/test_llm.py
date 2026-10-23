import json
import unittest
from unittest.mock import MagicMock, patch
from urllib.error import URLError

from llm import chat


class LocalModelTests(unittest.TestCase):
    @patch("llm.build_opener")
    def test_loopback_contract(self, factory):
        response = MagicMock()
        response.__enter__.return_value.read.return_value = json.dumps({"message": {"content": "{}"}}).encode()
        factory.return_value.open.return_value = response
        self.assertEqual(chat("test-model", "rules", "brief"), "{}")
        request = factory.return_value.open.call_args.args[0]
        self.assertEqual(request.full_url, "http://127.0.0.1:11434/api/chat")
        self.assertFalse(json.loads(request.data)["stream"])

    @patch("llm.build_opener")
    def test_offline_is_explicit(self, factory):
        factory.return_value.open.side_effect = URLError("offline")
        with self.assertRaises(RuntimeError):
            chat("test-model", "rules", "brief")

    def test_empty_model_rejected(self):
        with self.assertRaises(RuntimeError):
            chat("", "rules", "brief")


if __name__ == "__main__":
    unittest.main()
