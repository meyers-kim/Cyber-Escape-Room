from escaperoom.rooms.base import Room
from escaperoom import utils


class VaultRoom(Room):
    """Vault Corridor room for regex search and validation.
    
    This room requires players to find a SAFE{a-b-c} pattern in a text dump
    where the checksum a+b==c is satisfied.
    """
    
    name = "vault"

    def enter(self, state):
        """Display room entry message.
        
        Args:
            state: Current game state object.
            
        Returns:
            str: Room description and available items.
        """
        return (
            "Dear student, you find yourself in the vault corridor full of "
            "messy dumps.\n"
            "\n"
            "Item you can see: vault_dump.txt"
        )

    def inspect(self, item, state, tr):
        """Inspect vault dump to find valid SAFE code.
        
        Uses regex to find SAFE{a-b-c} patterns and validates them with
        checksum a+b==c. The first valid code becomes the token.
        
        Args:
            item: Item name to inspect.
            state: Game state object to store token.
            tr: Transcript logger for evidence recording.
            
        Returns:
            str: Analysis steps and results.
        """
        if item != "vault_dump.txt":
            return "The only file here is 'vault_dump.txt'."

        steps = []
        steps.append("[VAULT] reading data/vault_dump.txt ...")
        text = utils.read_text("data/vault_dump.txt")

        steps.append(
            "[VAULT] scanning for SAFE{a-b-c} patterns "
            "(regex tolerant to spaces/newlines)"
        )
        triples = utils.regex_find_safe_all(text)
        if not triples:
            return "[VAULT] no SAFE patterns found."

        steps.append(
            f"[VAULT] {len(triples)} candidate(s) found, "
            f"checking a+b==c ..."
        )
        
        # Find first valid checksum
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
        """Provide hint for solving the room.
        
        Args:
            state: Current game state object.
            
        Returns:
            str: Hint message.
        """
        return (
            "Try: inspect vault_dump.txt\n"
            "We find all SAFE{a-b-c} and validate where a+b==c. "
            "The first valid one becomes the token a-b-c."
        )
