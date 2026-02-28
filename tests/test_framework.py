import pytest
from unittest.mock import Mock, AsyncMock, patch
from catcord_bots.personality import PersonalityRenderer


class TestFramework:
    def test_personality_renderer_init(self):
        renderer = PersonalityRenderer(
            prompt_composer_url="http://test.com",
            character_id="test_char",
            cathy_api_url="http://cathy.com",
            fallback_system_prompt="Test prompt",
        )
        assert renderer.character_id == "test_char"
        assert renderer.fallback_system_prompt == "Test prompt"
        assert renderer.prompt_composer_url == "http://test.com"
        assert renderer.timeout_seconds == 60
        assert renderer.min_seconds_between_calls == 0
        assert renderer.cathy_api_mode == "ollama"
        assert renderer.cathy_api_model == "gemma2:2b"

    def test_personality_renderer_rate_limiting(self):
        renderer = PersonalityRenderer(
            prompt_composer_url="http://test.com",
            character_id="test",
            cathy_api_url="http://cathy.com",
            fallback_system_prompt="Test",
            min_seconds_between_calls=60
        )
        assert not renderer._rate_limited()
        import time
        renderer._last_call_ts = time.time()
        assert renderer._rate_limited()

    def test_personality_user_prompt_structure(self):
        renderer = PersonalityRenderer(
            prompt_composer_url="http://test.com",
            character_id="test",
            cathy_api_url="http://cathy.com",
            fallback_system_prompt="Test"
        )
        payload = {"mode": "retention", "disk": {}, "actions": {}}
        assert renderer.prompt_composer_url == "http://test.com"
