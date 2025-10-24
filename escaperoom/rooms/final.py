from escaperoom.rooms.base import Room
import sys

class FinalGateRoom(Room):
    name = "final"

    def enter(self, state):
        return (
            "Final Gate.\n"
            "First, inspect the gate file to prepare your proof.\n"
            "\n"
            "Item you can see: final_gate.txt"
        )

    def inspect(self, item, state, tr):
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
        # hint only says the next steps
        return (
            "Try: inspect final_gate.txt\n"
            "Then: use gate (only works if all tokens are present)."
        )