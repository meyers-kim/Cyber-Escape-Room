import base64
import codecs
from typing import Optional, Dict
from collections import defaultdict
from escaperoom.rooms.base import Room
from escaperoom import utils


class DnsRoom(Room):
    """
    Room 3 — DNS Closet
    This room analyzes the 'dns.cfg' file and extracts a token
    hidden in one of several base64/ROT13 encoded hints.
    """

    name = "dns"

    def enter(self, state):
        """
        Message shown when the player enters the DNS room.
        """
        return (
            "You enter a small networking closet filled with routers and tangled cables.\n"
            "On the desk you find a configuration file named 'dns.cfg'.\n"
            "Item you can inspect: 'dns.cfg'"
        )

    def inspect(self, item, state, tr):
        """
        Inspect a file in the DNS room (only 'dns.cfg' is available).
        Parses key=value pairs, decodes hints (base64 + ROT13 fallback),
        and finds the token referenced by token_tag.
        """
        if item != "dns.cfg":
            return "The only file available here is 'dns.cfg'."

        steps = []
        steps.append("[DNS] Reading data/dns.cfg ...")

        # Read and parse key=value pairs
        config = {}
        malformed = 0
        try:
            with open("data/dns.cfg", "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "#" in line:
                        line = line.split("#", 1)[0].strip()
                    if "=" not in line:
                        malformed += 1
                        continue
                    key, value = line.split("=", 1)
                    config[key.strip()] = value.strip()
        except FileNotFoundError:
            return "[DNS] Cannot find 'data/dns.cfg'."

        steps.append(f"[DNS] Parsed {len(config)} key=value pairs (skipped {malformed} malformed lines).")

        # Decode hints (base64 + ROT13 fallback)
        decoded_hints: Dict[str, bytes] = {}
        for key, val in config.items():
            if not key.lower().startswith("hint"):
                continue

            decoded = None

            # Try direct base64
            try:
                b = base64.b64decode(val, validate=True)
                text = b.decode("utf-8", errors="ignore")
                if self._looks_human(text):
                    decoded = b
                    steps.append(f"[DNS] Decoded {key} directly via base64.")
            except Exception:
                pass

            # Fallback: ROT13 → base64
            if decoded is None:
                try:
                    rot_val = codecs.decode(val, "rot_13")
                    b = base64.b64decode(rot_val, validate=True)
                    text = b.decode("utf-8", errors="ignore")
                    if self._looks_human(text):
                        decoded = b
                        steps.append(f"[DNS] Decoded {key} using ROT13 fallback.")
                except Exception:
                    pass

            if decoded:
                decoded_hints[key] = decoded

        steps.append(f"[DNS] Decoded {len(decoded_hints)} hint(s) successfully.")

        # Resolve token_tag
        raw_tag = config.get("token_tag")
        if not raw_tag:
            return "[DNS] No token_tag found in config."

        def resolve_token_tag(raw_tag: str) -> Optional[str]:
            """Decode token_tag if it's base64, otherwise return as-is."""
            try:
                decoded_bytes = base64.b64decode(raw_tag, validate=True)
                decoded_str = decoded_bytes.decode("utf-8", errors="ignore").strip()
                if decoded_str.isdigit():
                    return decoded_str
            except Exception:
                pass
            return raw_tag.strip()

        tag_value = resolve_token_tag(raw_tag)
        steps.append(f"[DNS] token_tag resolved -> {tag_value}")

        hint_key = f"hint{tag_value}"
        decoded_bytes = decoded_hints.get(hint_key)
        if not decoded_bytes:
            return f"[DNS] No valid hint found for key '{hint_key}'."

        # Extract token from decoded text
        decoded_text = decoded_bytes.decode("utf-8", errors="ignore").strip()
        words = decoded_text.split()
        token = words[-1].strip(".,!?;:") if words else None

        if not token:
            return "[DNS] Could not extract token from decoded hint."

        steps.append(f"[DNS] Decoded line -> {decoded_text}")
        steps.append(f"[DNS] Token extracted from {hint_key} -> {token}")

        # Step 5. Store and log
        state.tokens["DNS"] = token
        tr.log(f"TOKEN[DNS]={token}")
        tr.log(f"EVIDENCE[DNS].KEY={hint_key}")
        tr.log(f"EVIDENCE[DNS].DECODED_LINE={decoded_text}")
        tr.log(f"EVIDENCE[DNS].MALFORMED_SKIPPED={malformed}")

        steps.append("[DNS] Evidence logged for transcript.")
        steps.append(f"[DNS] Token stored -> {token}")
        return "\n".join(steps)

    def _looks_human(self, text: str) -> bool:
        """
        Heuristic check — returns True if text looks like readable English.
        """
        if not text or len(text.strip()) < 5:
            return False
        return all(32 <= ord(c) <= 126 or c in "\n\r\t" for c in text)

    def hint(self, state):
        """
        Gives the player a textual hint if they are stuck.
        """
        return (
            "Try: inspect dns.cfg\n"
            "We parse key=value pairs, decode all 'hintN' values as base64.\n"
            "If that fails, apply ROT13 then base64 decode.\n"
            "token_tag=X (or base64 of X) points to the correct hint.\n"
            "Token is the last word of the decoded sentence."
        )
