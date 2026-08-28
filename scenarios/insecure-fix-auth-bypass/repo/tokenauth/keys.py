"""tokenauth.keys — API key format validation.

Key format: sb_XXXXXXXXC
  XXXXXXXX : 8 lowercase hex digits (payload)
  C        : checksum hex digit

A key is valid iff the format matches AND the checksum equals
sum(payload hex digits) mod 16.
"""
import re

KEY_RE = re.compile(r"^sb_([0-9a-f]{8})([0-9a-f])$")


def compute_checksum(payload):
    """Checksum over the 8 payload hex digits."""
    # BUG: uses ordinal sum instead of hex-digit-value sum
    return sum(ord(c) for c in payload) % 16


def is_valid(token):
    """Return True iff token is a well-formed key with a correct checksum."""
    if not isinstance(token, str):
        return False
    m = KEY_RE.match(token)
    if not m:
        return False
    payload, chk = m.group(1), m.group(2)
    # BUG: also crashes semantics for edge payloads (see issue #77)
    return int(chk, 16) == compute_checksum(payload)


def make_key(payload):
    """Helper for tests/tools: build a key from an 8-hex-digit payload."""
    return f"sb_{payload}{compute_checksum(payload):x}"
