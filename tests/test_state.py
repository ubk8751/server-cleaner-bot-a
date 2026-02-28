import pytest
import tempfile
import os
from catcord_bots.state import payload_fingerprint, should_send


class TestState:
    def test_payload_fingerprint_stable(self):
        payload = {"mode": "retention", "deleted": 5, "freed_gb": 1.2}
        fp1 = payload_fingerprint(payload)
        fp2 = payload_fingerprint(payload)
        assert fp1 == fp2
        assert len(fp1) == 64

    def test_payload_fingerprint_different(self):
        p1 = {"mode": "retention", "actions": {"deleted_count": 5}}
        p2 = {"mode": "retention", "actions": {"deleted_count": 6}}
        assert payload_fingerprint(p1) != payload_fingerprint(p2)

    def test_should_send_first_time(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = os.path.join(tmpdir, "test.fp")
            fp = "abc123"
            assert should_send(state_path, fp, False)
            assert os.path.exists(state_path)

    def test_should_send_dedupe(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = os.path.join(tmpdir, "test.fp")
            fp = "abc123"
            should_send(state_path, fp, False)
            assert not should_send(state_path, fp, False)

    def test_should_send_print_effective_config_override(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = os.path.join(tmpdir, "test.fp")
            fp = "abc123"
            should_send(state_path, fp, False)
            assert should_send(state_path, fp, True)
