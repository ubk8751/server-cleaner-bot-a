#!/usr/bin/env python3
"""Standalone test for prefix normalization logic."""
import re


def normalize_prefix(raw: str) -> str:
    """Normalize raw prefix."""
    text = raw.strip()
    if text.startswith('"') and text.endswith('"'):
        text = text[1:-1]
    elif text.startswith("'") and text.endswith("'"):
        text = text[1:-1]
    return text.strip()


def validate_prefix(text: str) -> tuple[bool, str]:
    """Validate AI prefix is safe and contains no numbers."""
    t = text.strip()
    tlow = t.lower()

    if not t:
        return False, "empty"

    bad_ack = ["ok", "understood", "please provide"]
    if any(tlow.startswith(x) for x in bad_ack):
        return False, "acknowledgement/assistant filler"

    banned = ["today", "yesterday", "uptime", "since", "operational since", "elapsed"]
    for b in banned:
        if re.search(rf"\b{re.escape(b)}\b", tlow):
            return False, f"banned phrase '{b}'"

    if re.search(r"\d", t):
        return False, "contains digits"

    bad_actions = ["deleted", "removed", "purged", "redacted", "cleared"]
    if any(w in tlow for w in bad_actions):
        return False, "claims deletion"

    return True, ""


def test_normalization():
    """Test prefix normalization pipeline."""
    print("Testing normalization...")
    
    cases = [
        ('"System operational"', "System operational"),
        ("'All systems green'", "All systems green"),
        ("  Whitespace  ", "Whitespace"),
        ('"Quoted text"', "Quoted text"),
        ("Multi\nline\ntext", "Multi\nline\ntext"),
        ("Everything running smoothly. No issues detected.", "Everything running smoothly. No issues detected."),
    ]
    
    for raw, expected in cases:
        result = normalize_prefix(raw)
        status = "✓" if result == expected else "✗"
        print(f"  {status} normalize({raw!r})")
        print(f"      -> {result!r}")
        if result != expected:
            print(f"      Expected: {expected!r}")
            return False
    
    print("✓ All normalization tests passed\n")
    return True


def test_validation():
    """Test prefix validation rules."""
    print("Testing validation...")
    
    valid = [
        "System operational.",
        "All systems green!",
        "Status nominal?",
        "Maintenance complete;",
        "Everything running smoothly.",
        "Multi\nline\ntext is allowed",
        "x" * 200,
    ]
    
    invalid = [
        ("", "empty"),
        ("Contains 123 digits", "contains digits"),
        ("Deleted files", "claims deletion"),
        ("Today is good", "banned phrase 'today'"),
        ("Uptime is high", "banned phrase 'uptime'"),
        ("ok", "acknowledgement/assistant filler"),
        ("Since yesterday", "banned phrase 'since'"),
    ]
    
    for text in valid:
        ok, reason = validate_prefix(text)
        status = "✓" if ok else "✗"
        display = text if len(text) < 40 else text[:37] + "..."
        print(f"  {status} valid: {display!r}")
        if not ok:
            print(f"      Unexpected rejection: {reason!r}")
            return False
    
    for text, expected_reason in invalid:
        ok, reason = validate_prefix(text)
        status = "✓" if not ok else "✗"
        display = text if len(text) < 40 else text[:37] + "..."
        print(f"  {status} invalid: {display!r} -> {reason!r}")
        if ok:
            print(f"      Should have been rejected")
            return False
    
    print("✓ All validation tests passed\n")
    return True


def test_pipeline():
    """Test full normalization + validation pipeline."""
    print("Testing full pipeline (normalize -> validate)...")
    
    cases = [
        ('"Everything running smoothly. No issues detected."', True, "Everything running smoothly. No issues detected."),
        ('"System operational"', True, "System operational"),
        ('"Deleted 5 files"', False, None),
        ('"Today everything is fine"', False, None),
        ('Multi\nline\nresponse', True, "Multi\nline\nresponse"),
    ]
    
    for raw, should_pass, expected_normalized in cases:
        normalized = normalize_prefix(raw)
        ok, reason = validate_prefix(normalized)
        
        status = "✓" if ok == should_pass else "✗"
        print(f"  {status} {raw!r}")
        print(f"      normalized: {normalized!r}")
        print(f"      valid: {ok} ({reason if not ok else 'passed'})")
        
        if ok != should_pass:
            print(f"      Expected valid={should_pass}")
            return False
        
        if should_pass and expected_normalized and normalized != expected_normalized:
            print(f"      Expected: {expected_normalized!r}")
            return False
    
    print("✓ All pipeline tests passed\n")
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("Prefix Normalization & Validation Test Suite")
    print("=" * 60 + "\n")
    
    all_passed = True
    all_passed &= test_normalization()
    all_passed &= test_validation()
    all_passed &= test_pipeline()
    
    print("=" * 60)
    if all_passed:
        print("✅ ALL TESTS PASSED")
    else:
        print("❌ SOME TESTS FAILED")
    print("=" * 60)
