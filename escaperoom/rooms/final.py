from escaperoom.rooms.base import Room

class FinalGateRoom(Room):
    name = "final"

    def enter(self, state):
        return (
            "The final gate wants a message with all tokens in the right order.\n"
            "Item that you can see: final_gate.txt"
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
        ordered_values = []
        for key in order:
            ordered_values.append(state.tokens.get(key, "?"))

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
            return "You did not collect all tokens yet, but message is printed for checking."
        return "Final proof printed."

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
        if item.strip().lower() in ("gate", "final", "final_gate"):
            return self.inspect("final_gate.txt", state, tr)
        return "nothing to use with that here."
    
    def hint(self, state):
        return "Try: inspect final_gate.txt or use gate"