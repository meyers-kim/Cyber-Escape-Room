class Room:
    # this is just the base class others will inherit from

    name = "abstract"

    def enter(self, state):
        # what happens when you enter a room
        raise NotImplementedError("not done yet")

    def inspect(self, item, state, tr):
        # called when player inspects an item or file
        raise NotImplementedError("not done yet")

    def use(self, item, state, tr):
        # not needed now
        return "nothing happens here"