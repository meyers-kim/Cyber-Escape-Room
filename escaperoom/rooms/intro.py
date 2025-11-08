"""Intro room for the game.
This is the lobby that explains the goal and basic flow."""

from escaperoom.rooms.base import Room

class IntroRoom(Room):
    """Starting lobby of the escape room.
    Tells the player where to go next and how to interact.
    No file to see here here."""

    name = "intro"

    def enter(self, state):
        """Shows a short welcome message.
        Tells the player where he can go."""
        return (
            "Dear student, you find yourself in the intro lobby of our cyber escape room.\n"
            "You are supposed to explore the other rooms and gather four tokens to open the final gate.\n"
            "Rooms you can enter: soc, dns, vault, malware, final.\n"
        )

    def inspect(self, item, state, tr):
        """Nothing to inspect in the lobby.
        So the default from the base class gets returned."""
        return super().inspect(item, state, tr)
    
    def hint(self, state):
        """Tell the player what to do: move to a room and inspect the file."""
        return (
            "Try next: move soc  |  move dns  |  move vault  |  move malware  |  move final\n"
            "Goal: each room has exactly one file to inspect (auth.log, dns.cfg, vault_dump.txt, proc_tree.jsonl, final_gate.txt).\n"
            "Run 'inspect <file>' in each room to extract a token."
        )
        
    def use(self, item, state, tr):
        """Nothing to use in the lobby.
        So the default from the base class gets returned."""
        return super().use(item, state, tr)