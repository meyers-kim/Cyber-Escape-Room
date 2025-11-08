import os
import re
import json
import base64
import codecs

# File I/O Utilities

def read_lines(path):
    """Read file and return list of lines without newline characters.
    
    Args:
        path: File path to read.
        
    Returns:
        list: List of lines with trailing newlines removed, or empty list
            if file not found.
    """
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return [ln.rstrip("\n") for ln in f]
    except FileNotFoundError:
        return []


def read_text(path):
    """Read entire file content as a single string.
    
    Args:
        path: File path to read.
        
    Returns:
        str: Complete file content, or empty string if file not found.
    """
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except FileNotFoundError:
        return ""


def jsonl_iter(path):
    """Iterate over JSONL file, yielding parsed JSON objects.
    
    Args:
        path: Path to JSONL file (one JSON object per line).
        
    Yields:
        dict: Parsed JSON objects from each non-empty line.
    """
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            for ln in f:
                ln = ln.strip()
                if not ln:
                    continue
                try:
                    yield json.loads(ln)
                except Exception:
                    continue
    except FileNotFoundError:
        return


# Encoding/Decoding

def b64_decode(s):
    """Decode base64 string with automatic padding.
    
    Args:
        s: Base64-encoded string.
        
    Returns:
        str: Decoded UTF-8 string, or empty string if decoding fails.
    """
    if not s:
        return ""
    try:
        pad = "=" * (-len(s) % 4)
        raw = base64.b64decode((s + pad).encode("utf-8"), validate=False)
        return raw.decode("utf-8", errors="replace")
    except Exception:
        return ""


def rot13(s):
    """Apply ROT13 cipher to string.
    
    Args:
        s: String to encode/decode.
        
    Returns:
        str: ROT13 transformed string, or original if transformation fails.
    """
    try:
        return codecs.decode(s, "rot_13")
    except Exception:
        return s


def looks_human(txt):
    """Check if text appears to be human-readable.
    
    Args:
        txt: Text to evaluate.
        
    Returns:
        bool: True if text is mostly printable ASCII and contains spaces.
    """
    if not txt:
        return False
    printable = set("".join(map(chr, range(32, 127))) + "\t\n\r")
    good = sum(1 for ch in txt if ch in printable)
    ratio = good / max(1, len(txt))
    return (ratio > 0.9) and (" " in txt)


# DNS & Parsing

def parse_kv_file(path):
    """Parse key-value configuration file.
    
    Reads file with format 'key=value', ignoring empty lines and comments.
    
    Args:
        path: Path to configuration file.
        
    Returns:
        dict: Dictionary mapping keys to values.
    """
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
    """Resolve DNS token tag from various formats.
    
    Token tag can be:
    - Direct format: 'hint3'
    - Base64-encoded number: 'NQ==' -> 'hint5'
    - Base64-encoded hint: base64('hint6') -> 'hint6'
    
    Args:
        raw_tag: Raw token tag string.
        
    Returns:
        str: Resolved hint tag in format 'hintN' or original tag.
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


# SOC/Network Analysis

_ipv4_re = re.compile(
    r"\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}"
    r"(?:25[0-5]|2[0-4]\d|1?\d?\d)\b"
)


def find_ips_in_line(line):
    """Extract first IPv4 address from text line.
    
    Args:
        line: Text line to search.
        
    Returns:
        str: First IPv4 address found, or None if no match.
    """
    m = _ipv4_re.search(line or "")
    return m.group(0) if m else None


def cidr24_of_ip(ip):
    """Convert IP address to /24 CIDR notation.
    
    Args:
        ip: IPv4 address string (e.g., '192.168.1.100').
        
    Returns:
        str: CIDR /24 network (e.g., '192.168.1.0/24'), or None if invalid.
    """
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
    """Extract last octet from IPv4 address.
    
    Args:
        ip: IPv4 address string.
        
    Returns:
        int: Last octet value (0-255), or None if invalid.
    """
    try:
        n = int(ip.split(".")[-1])
        if 0 <= n <= 255:
            return n
        return None
    except Exception:
        return None


# Vault Pattern Matching

SAFE_RE = re.compile(
    r"S\s*A\s*F\s*E\s*\{\s*([0-9]+)\s*[-]\s*([0-9]+)\s*[-]\s*([0-9]+)\s*\}",
    re.IGNORECASE | re.MULTILINE,
)


def regex_find_safe_all(text):
    """Find all SAFE{a-b-c} patterns in text.
    
    Regex is tolerant to spaces/newlines between characters.
    
    Args:
        text: Text to search for SAFE patterns.
        
    Returns:
        list: List of tuples (a, b, c) containing numeric values.
    """
    triples = []
    for m in SAFE_RE.finditer(text or ""):
        try:
            a, b, c = int(m.group(1)), int(m.group(2)), int(m.group(3))
            triples.append((a, b, c))
        except Exception:
            continue
    return triples


# Malware Analysis

def is_exfil_command(cmd):
    """Check if command is a data exfiltration command.
    
    Treats command as exfiltration if:
    - First token is 'curl' or 'scp'
    - Contains ' curl http' or ' curl https'
    
    Args:
        cmd: Command string to analyze.
        
    Returns:
        bool: True if command appears to be exfiltration attempt.
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
