import json
from unittest.mock import MagicMock, patch

from django.test import TestCase, override_settings


class MCPViewTests(TestCase):
    endpoint = "/mcp/"

    def _post(self, payload):
        return self.client.post(
            self.endpoint,
            data=json.dumps(payload),
            content_type="application/json",
        )

    def test_only_post_allowed(self):
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, 405)

    def test_list_interactions_returns_fake_records(self):
        response = self._post({"id": "1", "method": "interactions.list", "params": {}})
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["jsonrpc"], "2.0")
        self.assertEqual(body["result"]["type"], "resources.list")
        self.assertGreaterEqual(len(body["result"]["resources"]), 1)

    def test_get_interaction_requires_identifier(self):
        response = self._post({"id": "2", "method": "interactions.get", "params": {}})
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIn("error", body)
        self.assertEqual(body["error"]["code"], 400)

    @override_settings(OPENAI_API_KEY="test-key", OPENAI_BASE_URL="https://example.com", OPENAI_MODEL="gpt-mock")
    @patch("interactions.views.OpenAI")
    def test_generate_interaction_invokes_openai_client(self, mock_openai):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.model_dump.return_value = {"output": "hello world"}
        mock_client.responses.create.return_value = mock_response
        mock_openai.return_value = mock_client

        payload = {
            "id": "3",
            "method": "interactions.generate",
            "params": {"record_id": 1, "prompt": "Say hi"},
        }
        response = self._post(payload)

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIn("result", body)
        self.assertEqual(body["result"]["type"], "interactions.generate")
        self.assertEqual(body["result"]["openai_response"], {"output": "hello world"})

        mock_openai.assert_called_once_with(api_key="test-key", base_url="https://example.com")
        mock_client.responses.create.assert_called_once_with(model="gpt-mock", input="Say hi")

    def test_generate_interaction_without_api_key_returns_error(self):
        payload = {"id": "4", "method": "interactions.generate", "params": {"record_id": 1}}
        response = self._post(payload)
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIn("error", body)
        self.assertEqual(body["error"]["code"], 503)
        self.assertIn("OPENAI_API_KEY", body["error"]["message"])
