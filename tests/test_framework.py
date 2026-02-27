import pytest
from unittest.mock import Mock, AsyncMock, patch
from catcord_bots.ai_summary import AISummaryRenderer


class TestFramework:
    def test_ai_summary_renderer_init(self):
        renderer = AISummaryRenderer(
            characters_api_url="http://test.com",
            character_id="test_char",
            cathy_api_url="http://cathy.com",
            fallback_system_prompt="Test prompt"
        )
        assert renderer.character_id == "test_char"
        assert renderer.fallback_system_prompt == "Test prompt"
        assert renderer.timeout_seconds == 6
        assert renderer.min_seconds_between_calls == 30

    def test_ai_summary_renderer_rate_limiting(self):
        renderer = AISummaryRenderer(
            characters_api_url="http://test.com",
            character_id="test",
            cathy_api_url="http://cathy.com",
            fallback_system_prompt="Test",
            min_seconds_between_calls=60
        )
        assert not renderer._rate_limited()
        renderer._last_call_ts = 999999999
        assert renderer._rate_limited()

    def test_ai_summary_user_prompt_structure(self):
        renderer = AISummaryRenderer(
            characters_api_url="http://test.com",
            character_id="test",
            cathy_api_url="http://cathy.com",
            fallback_system_prompt="Test"
        )
        payload = {"test": "data", "count": 5}
        prompt = renderer._build_user_prompt(payload)
        assert "JSON:" in prompt
        assert "STRICT RULES:" in prompt
        assert "Do NOT invent" in prompt
        assert '"test": "data"' in prompt
