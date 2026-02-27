"""State management for deduplication."""
import hashlib
import json
import os
from typing import Dict, Any


def payload_fingerprint(payload: Dict[str, Any]) -> str:
    """Generate stable hash from payload."""
    s = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def should_send(state_path: str, fp: str, debug: bool, force_notify: bool) -> bool:
    """Check if message should be sent based on dedupe state.
    
    :param state_path: Path to state file
    :type state_path: str
    :param fp: Fingerprint of current payload
    :type fp: str
    :param debug: Debug mode (always send)
    :type debug: bool
    :param force_notify: Force notification (always send)
    :type force_notify: bool
    :return: True if should send
    :rtype: bool
    """
    if debug or force_notify:
        return True
    
    prev = None
    if os.path.exists(state_path):
        with open(state_path, "r") as f:
            prev = f.read().strip() or None
    
    if prev == fp:
        return False
    
    os.makedirs(os.path.dirname(state_path), exist_ok=True)
    with open(state_path, "w") as f:
        f.write(fp)
    return True
