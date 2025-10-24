from escaperoom.rooms.base import Room

class IntroRoom(Room):
    name = "intro"

    def enter(self, state):
        return (
            "Dear student, you find yourself in the intro lobby of our cyber escape room.\n"
            "You are supposed to explore the other rooms and gather four tokens to open the final gate.\n"
            "Rooms you can enter: soc, dns, vault, malware, final.\n"
        )

    def inspect(self, item, state, tr):
        return "Nothing to inspect here. Try 'move soc' or type 'hint'."
    
    def hint(self, state):
        return (
            "Try next: move soc  |  move dns  |  move vault  |  move malware  |  move final\n"
            "Goal: each room has exactly one file to inspect (auth.log, dns.cfg, vault_dump.txt, proc_tree.jsonl, final_gate.txt).\n"
            "Run 'inspect <file>' in each room to extract a token."
        )
        
    def use(self, item, state, tr):
        if item.strip().lower() in ("terminal", "console", "pc"):
            return "The terminal says: type 'help' to see commands."
        return "nothing to use here."