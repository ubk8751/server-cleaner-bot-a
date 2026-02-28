"""Core functionality tests for PersonalityRenderer."""
import pytest
from catcord_bots.personality import PersonalityRenderer


class TestPersonalityRenderer:
    """Test suite for PersonalityRenderer class."""

    def test_normalize_prefix_removes_quotes(self) -> None:
        """Test that normalization removes wrapping quotes."""
        renderer = PersonalityRenderer(
            prompt_composer_url="http://test",
            character_id="test",
            cathy_api_url="http://test",
            fallback_system_prompt="test",
        )
        
        assert renderer._normalize_prefix('"test"') == "test"
        assert renderer._normalize_prefix("'test'") == "test"
        assert renderer._normalize_prefix("test") == "test"

    def test_validate_prefix_rejects_invalid(self) -> None:
        """Test that validation rejects invalid prefixes."""
        renderer = PersonalityRenderer(
            prompt_composer_url="http://test",
            character_id="test",
            cathy_api_url="http://test",
            fallback_system_prompt="test",
        )
        
        assert not renderer._validate_prefix("")[0]
        assert not renderer._validate_prefix("Contains 123")[0]
        assert not renderer._validate_prefix("I am a bot")[0]
        assert not renderer._validate_prefix("Matrix room")[0]

    def test_validate_prefix_accepts_valid(self) -> None:
        """Test that validation accepts valid prefixes."""
        renderer = PersonalityRenderer(
            prompt_composer_url="http://test",
            character_id="test",
            cathy_api_url="http://test",
            fallback_system_prompt="test",
        )
        
        assert renderer._validate_prefix("Logs clear, Master.")[0]
        assert renderer._validate_prefix("Storage getting tight, Master.")[0]
        assert renderer._validate_prefix("Cleanup executed, Master.")[0]

    def test_fallback_prefix_logic(self) -> None:
        """Test fallback prefix selection logic."""
        renderer = PersonalityRenderer(
            prompt_composer_url="http://test",
            character_id="test",
            cathy_api_url="http://test",
            fallback_system_prompt="test",
        )
        
        payload_no_action_healthy = {
            "actions": {"deleted_count": 0},
            "storage_status": "healthy"
        }
        assert renderer._get_fallback_prefix(payload_no_action_healthy) == "Logs clear, Master."
        
        payload_no_action_tight = {
            "actions": {"deleted_count": 0},
            "storage_status": "tight"
        }
        assert renderer._get_fallback_prefix(payload_no_action_tight) == "Storage getting tight, Master."
        
        payload_with_action = {
            "actions": {"deleted_count": 5},
            "storage_status": "healthy"
        }
        assert renderer._get_fallback_prefix(payload_with_action) == "Cleanup executed, Master."

    def test_rate_limiting(self) -> None:
        """Test rate limiting functionality."""
        renderer = PersonalityRenderer(
            prompt_composer_url="http://test",
            character_id="test",
            cathy_api_url="http://test",
            fallback_system_prompt="test",
            min_seconds_between_calls=10,
        )
        
        assert not renderer._rate_limited()
        assert renderer._rate_limited()
