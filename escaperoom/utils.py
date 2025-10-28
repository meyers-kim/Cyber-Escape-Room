import os
import re
import json
import base64
import codecs

# -------------- file i/o ----------------

def read_lines(path):
    # read file safely, return list of lines (with \n removed)
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return [ln.rstrip("\n") for ln in f]
    except FileNotFoundError:
        return []

def read_text(path):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except FileNotFoundError:
        return ""

def jsonl_iter(path):
    # iterate json per line, skip broken ones
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            for ln in f:
                ln = ln.strip()
                if not ln:
                    continue
                try:
                    yield json.loads(ln)
                except Exception:
                    # ignore malformed json line
                    continue
    except FileNotFoundError:
        return

# -------------- base64 / rot13 / text checks --------------

def b64_decode(s):
    # decode base64 to str; return "" on fail
    if not s:
        return ""
    try:
        # allow missing padding
        pad = "=" * (-len(s) % 4)
        raw = base64.b64decode((s + pad).encode("utf-8"), validate=False)
        return raw.decode("utf-8", errors="replace")
    except Exception:
        return ""

def rot13(s):
    try:
        return codecs.decode(s, "rot_13")
    except Exception:
        return s

def looks_human(txt):
    # rough check: mostly printable and has at least one space (so likely a sentence)
    if not txt:
        return False
    printable = set("".join(map(chr, range(32, 127))) + "\t\n\r")
    good = sum(1 for ch in txt if ch in printable)
    ratio = good / max(1, len(txt))
    return (ratio > 0.9) and (" " in txt)

# -------------- kv parsing used by dns + final --------------

def parse_kv_file(path):
    # parse simple key=value files, ignore comments (#) and empty lines
    out = {}
    for raw in read_lines(path):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip()
    return out

def resolve_token_tag(raw_tag):
    """
    dns token_tag can be:
      - 'hint3'
      - base64 of a number (NQ== -> 5)   -> returns 'hint5'
      - base64 of 'hint6'                -> returns 'hint6'
    """
    if not raw_tag:
        return ""
    tag = raw_tag.strip().lower()
    if tag.startswith("hint"):
        return tag
    dec = b64_decode(raw_tag).strip().lower()
    if not dec:
        return tag
    if dec.isdigit():
        return f"hint{int(dec)}"
    if dec.startswith("hint"):
        return dec
    return tag

# -------------- IP helpers used by SOC room --------------

_ipv4_re = re.compile(
    r"\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)\b"
)

def find_ips_in_line(line):
    m = _ipv4_re.search(line or "")
    return m.group(0) if m else None

def cidr24_of_ip(ip):
    try:
        parts = [int(x) for x in ip.split(".")]
        if len(parts) != 4:
            return None
        for p in parts:
            if p < 0 or p > 255:
                return None
        return f"{parts[0]}.{parts[1]}.{parts[2]}.0/24"
    except Exception:
        return None

def ip_last_octet(ip):
    try:
        n = int(ip.split(".")[-1])
        if 0 <= n <= 255:
            return n
        return None
    except Exception:
        return None

# -------------- regex for vault room --------------

# tolerate spaces/newlines between pieces, also weird unicode spaces
SAFE_RE = re.compile(
    r"S\s*A\s*F\s*E\s*\{\s*([0-9]+)\s*[-]\s*([0-9]+)\s*[-]\s*([0-9]+)\s*\}",
    re.IGNORECASE | re.MULTILINE,
)

def regex_find_safe_all(text):
    triples = []
    for m in SAFE_RE.finditer(text or ""):
        try:
            a, b, c = int(m.group(1)), int(m.group(2)), int(m.group(3))
            triples.append((a, b, c))
        except Exception:
            continue
    return triples

# -------------- malware helpers --------------

def is_exfil_command(cmd):
    """
    treat it as exfil if:
      - first token is 'curl' or 'scp', OR
      - obvious ' curl http' / ' curl https' appears
    """
    if not cmd:
        return False
    c_low = cmd.strip().lower()
    if not c_low:
        return False
    head = c_low.split()[0]
    if head in ("curl", "scp"):
        return True
    return (" curl http" in c_low) or (" curl https" in c_low)