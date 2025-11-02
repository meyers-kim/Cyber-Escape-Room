"""Final Gate room for the game.
Reads final_gate.txt, builds the proof message from tokens, and prints the 3 lines.
We show the expected hex from the file."""

import sys
from escaperoom.rooms.base import Room

class FinalGateRoom(Room):
    """Final step of the escape room.
    We read a config, assemble tokens in order, and mark the gate as pending.
    If any token is missing, we keep the gate locked and guide the player."""

    name = "final"

    def enter(self, state):
        """Shows a short description for the final room.
        Tells the player to inspect the gate file to start the proof."""

        return (
            "You stand in the final room in front of the gate.\n"
            "First, inspect the gate file to prepare your proof.\n"
            "\n"
            "Item you can see: final_gate.txt"
        )

    def inspect(self, item, state, tr):
        """Parses final_gate.txt and builds the proof message.
        Prints the three required lines and logs them to the transcript.
        If some token is missing it tells the player to collect all tokens."""

        if item not in ("final_gate.txt", "gate"):
            return "use: inspect final_gate.txt"

        data = self._parse_gate_file("data/final_gate.txt")
        if not data:
            return "final_gate.txt missing or broken"

        group_id = data.get("group_id", "unknown")
        order_raw = data.get("token_order", "")
        expected_hmac = data.get("expected_hmac", "")

        # order
        order = [x.strip() for x in order_raw.split(",") if x.strip()]
        if not order:
            return "token_order not set in final_gate.txt"

        # collect token
        ordered_values = [state.tokens.get(key, "?") for key in order]
        msg = f"{group_id}|{'-'.join(ordered_values)}"

        # print and log
        line1 = "FINAL_GATE=PENDING"
        line2 = f"MSG={msg}"
        line3 = f"EXPECTED_HMAC={expected_hmac}"

        print(line1)
        print(line2)
        print(line3)

        tr.log(line1)
        tr.log(line2)
        tr.log(line3)

        # small hint if not all tokens there
        if "?" in ordered_values:
            state.flags["final_ready"] = False
            return (
                "The gate file was inspected and the message was built,\n"
                "but some tokens are missing (shown as '?'). Collect all four tokens first."
            )

        state.flags["final_ready"] = True
        return (
            "Proof prepared. The gate starts shining.\n"
            "Now you can finally use the gate to escape."
        )

    def _parse_gate_file(self, path):
        """Reads a  key value file.
        Skips comments and empty lines, returns a dict with the values.
        If the file is missing, returns None instead of crashing."""

        out = {}
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                for raw in f:
                    line = raw.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" not in line:
                        continue
                    k, v = line.split("=", 1)
                    out[k.strip()] = v.strip()
        except FileNotFoundError:
            return None
        return out
    
    def use(self, item, state, tr):
        """Opens the gate only after a successful inspect with all tokens.
        Prints a final message, tries to close the transcript, and exits the program.
        If not ready, tells the player to inspect the file after collecting all tokens."""

        # only end if inspection succeeded and tokens were complete
        if item.strip().lower() in ("gate", "final", "final_gate"):
            if state.flags.get("final_ready"):
                # print a short closing line
                print(
                    "\nThe proof was accepted and the gate is opening! Well done.\n"
                )
                try:
                    tr.close()
                except Exception:
                    pass
                sys.exit(0)
            else:
                return "The gate remains locked. Inspect final_gate.txt after collecting all tokens."
        return "Nothing to use with that here."
    
    def hint(self, state):
        """Tells the player what to do: inspect the file and then use the gate."""
        return (
            "Try: inspect final_gate.txt\n"
            "Then: use gate (only works if all tokens are present)."
        )