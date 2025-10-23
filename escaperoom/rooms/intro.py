from escaperoom.rooms.base import Room

class IntroRoom(Room):
    name = "intro"

    def enter(self, state):
        text = (
            "Welcome to our Cyber Escape Room.\n"
            "This is the intro lobby. doors lead to: soc, dns, vault, malware, final.\n"
            "\n"
            "Items here: (none)\n"
            "Try: move soc | move dns | move vault | move malware | move final | hint"
        )
        return text

    def inspect(self, item, state, tr):
        return "nothing to inspect here yet."
    
    def hint(self, state):
        return (
            "Hint: each room has exactly one file: auth.log, dns.cfg, vault_dump.txt, proc_tree.jsonl.\n"
            "Inspect the file to get a token. then go to 'final' and use the gate."
        )
        
    def use(self, item, state, tr):
        if item.strip().lower() in ("terminal", "console", "pc"):
            return "The terminal says: type 'help' to see commands."
        return "nothing to use here."