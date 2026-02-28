"""Test PersonalityRenderer prefix normalization."""
from framework.catcord_bots.personality import PersonalityRenderer


def test_normalize_prefix():
    """Test prefix normalization pipeline."""
    renderer = PersonalityRenderer(
        prompt_composer_url="http://test",
        character_id="test",
        cathy_api_url="http://test",
        fallback_system_prompt="test",
    )
    
    cases = [
        ('"System operational"', "System operational."),
        ("'All systems green'", "All systems green."),
        ("Status nominal. Extra sentence.", "Status nominal."),
        ("Multi\nline\ntext", "Multi."),
        ("No punctuation", "No punctuation."),
        ("Already good!", "Already good!"),
        ("Question?", "Question?"),
        ("  Whitespace  ", "Whitespace."),
        ('"Quoted. Multiple."', "Quoted."),
        ("First; second", "First;"),
    ]
    
    for raw, expected in cases:
        result = renderer._normalize_prefix(raw)
        assert result == expected, f"normalize({raw!r}) = {result!r}, expected {expected!r}"
    
    print("✓ All normalization tests passed")


def test_validate_prefix():
    """Test prefix validation rules."""
    renderer = PersonalityRenderer(
        prompt_composer_url="http://test",
        character_id="test",
        cathy_api_url="http://test",
        fallback_system_prompt="test",
    )
    
    valid = [
        "System operational.",
        "All systems green!",
        "Status nominal?",
        "Maintenance complete;",
    ]
    
    invalid = [
        ("", "empty"),
        ("Contains 123 digits", "contains digits"),
        ("Deleted files", "claims deletion"),
        ("Today is good", "banned phrase 'today'"),
        ("Uptime is high", "banned phrase 'uptime'"),
        ("ok", "acknowledgement/assistant filler"),
        ("x" * 161, "too long"),
    ]
    
    for text in valid:
        ok, reason = renderer._validate_prefix(text)
        assert ok, f"Expected valid: {text!r}, got reason={reason!r}"
    
    for text, expected_reason in invalid:
        ok, reason = renderer._validate_prefix(text)
        assert not ok, f"Expected invalid: {text!r}"
        assert expected_reason in reason, f"Expected reason containing {expected_reason!r}, got {reason!r}"
    
    print("✓ All validation tests passed")


if __name__ == "__main__":
    test_normalize_prefix()
    test_validate_prefix()
    print("\n✓ All tests passed!")
