from escaperoom.rooms.base import Room

class IntroRoom(Room):
    name = "intro"

    def enter(self, state):
        text = (
            "You are in the intro room.\n"
            "paths go to: soc, dns, vault, malware.\n"
            "type 'move <room>' to go there."
        )
        return text

    def inspect(self, item, state, tr):
        return "nothing to inspect here yet."