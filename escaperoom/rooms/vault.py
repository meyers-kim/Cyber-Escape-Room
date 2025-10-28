from escaperoom.rooms.base import Room
from escaperoom import utils

class VaultRoom(Room):
    name = "vault"

    def enter(self, state):
        return (
            "Dear student, you find yourself in the vault corridor full of messy dumps.\n"
            "\n"
            "Item you can see: vault_dump.txt"
        )

    def inspect(self, item, state, tr):
        if item != "vault_dump.txt":
            return "The only file here is 'vault_dump.txt'."

        steps = []
        steps.append("[VAULT] reading data/vault_dump.txt ...")
        text = utils.read_text("data/vault_dump.txt")

        steps.append("[VAULT] scanning for SAFE{a-b-c} patterns (regex tolerant to spaces/newlines)")
        triples = utils.regex_find_safe_all(text)
        if not triples:
            return "[VAULT] no SAFE patterns found."

        steps.append(f"[VAULT] {len(triples)} candidate(s) found, checking a+b==c ...")
        good = None
        for a, b, c in triples:
            if a + b == c:
                good = (a, b, c)
                break

        if not good:
            return "[VAULT] patterns found but checksum failed for all."

        a, b, c = good
        token = f"{a}-{b}-{c}"
        state.tokens["SAFE"] = token

        tr.log(f"TOKEN[SAFE]={token}")
        tr.log(f'EVIDENCE[SAFE].MATCH="SAFE{{{a}-{b}-{c}}}"')
        tr.log(f"EVIDENCE[SAFE].CHECK={a}+{b}={c}")

        steps.append(f"[VAULT] valid code found -> SAFE{{{a}-{b}-{c}}}")
        steps.append(f"[VAULT] token -> {token}")
        return "\n".join(steps)

    def hint(self, state):
        return (
            "Try: inspect vault_dump.txt\n"
            "We find all SAFE{a-b-c} and validate where a+b==c. The first valid one becomes the token a-b-c."
        )