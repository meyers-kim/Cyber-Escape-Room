import re
from collections import defaultdict, Counter
from escaperoom.rooms.base import Room
from escaperoom import utils

class SocRoom(Room):
    """
    Room 2 — SOC Triage Desk 
    This room analyzes the 'auth.log' file and extracts a keypad token based on failed login attempts.
    """

    name = "soc"

    def enter(self, state):
        """
        Message shown when the player enters the SOC room.
        """
        return (
            "You step into the SOC triage desk.\n"
            "Screens flicker with login attempts and logs scrolling endlessly.\n"
            "Item you can inspect: 'auth.log'"
        )

    def inspect(self, item, state, tr):
        """
        Inspect a file in the SOC room (only 'auth.log' is available).
        Parses failed login attempts, groups them by /24 subnet,
        identifies the most attacked network, and generates a keypad token.
        """
        if item != "auth.log":
            return "The only file available here is 'auth.log'."

        steps = []
        steps.append("[SOC] Reading data/auth.log ...")

        # Use utils to read file (part of Escape Room engine)
        try:
            lines = utils.read_lines("data/auth.log")
        except FileNotFoundError:
            return "[SOC] Cannot find 'data/auth.log'."

        # Data structures
        failed_by_24 = Counter()
        failed_by_ip_in_24 = defaultdict(Counter)
        sample_for_24 = {}
        malformed = 0

        # Regex for IP extraction (backup if utils.find_ips_in_line fails)
        ip_regex = re.compile(r"(\d+\.\d+\.\d+\.\d+)")

        for line in lines:
            if "Failed password" not in line:
                continue

            # Try to extract IP via utils; fallback to regex if not found
            ip = utils.find_ips_in_line(line)
            if not ip:
                m = ip_regex.search(line)
                if not m:
                    malformed += 1
                    continue
                ip = m.group(1)

            # Compute /24 subnet
            cidr24 = utils.cidr24_of_ip(ip)
            if not cidr24:
                malformed += 1
                continue

            # Count failures
            failed_by_24[cidr24] += 1
            failed_by_ip_in_24[cidr24][ip] += 1

            if cidr24 not in sample_for_24:
                sample_for_24[cidr24] = line

        if not failed_by_24:
            return "[SOC] No failed password lines found in auth.log."

        # Determine top /24 by number of failures
        top24, count = failed_by_24.most_common(1)[0]
        steps.append(f"[SOC] Top /24 by failures → {top24} ({count} attempts)")

        # Determine most frequent IP within that /24
        ip_counts = failed_by_ip_in_24[top24]
        top_ip, ip_count = ip_counts.most_common(1)[0]
        steps.append(f"[SOC] Most active IP in {top24} → {top_ip} (x{ip_count})")

        # Extract last octet
        last_oct = utils.ip_last_octet(top_ip)
        if last_oct is None:
            return "[SOC] Couldn't parse the last octet of the selected IP."

        # Form token (KEYPAD)
        token = f"{last_oct}{count}"
        state.tokens["KEYPAD"] = token

        # Log evidence for transcript
        tr.log(f"TOKEN[KEYPAD]={token}")
        tr.log(f"EVIDENCE[KEYPAD].TOP24={top24}")
        tr.log(f"EVIDENCE[KEYPAD].COUNT={count}")
        tr.log(f"EVIDENCE[KEYPAD].SAMPLE={sample_for_24.get(top24, '')}")
        tr.log(f"EVIDENCE[KEYPAD].MALFORMED_SKIPPED={malformed}")

        steps.append(f"[SOC] Keypad code formed → {token}")
        steps.append("[SOC] Evidence logged for transcript.")
        return "\n".join(steps)

    def hint(self, state):
        """
        Gives the player a textual hint if they are stuck.
        """
        return (
            "Try: inspect auth.log\n"
            "Look for 'Failed password' lines in the log, group by /24 network,\n"
            "find the most attacked subnet, then the most frequent IP inside it.\n"
            "Token = last octet of that IP + number of failures in that /24."
        )