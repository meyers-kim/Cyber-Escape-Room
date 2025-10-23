class Room:
    # this is just the base class others will inherit from

    name = "abstract"

    def enter(self, state):
        # what happens when you enter a room
        raise NotImplementedError("not done yet")

    def inspect(self, item, state, tr):
        # called when player inspects an item or file
        raise NotImplementedError("inspect() not done yet")

    def use(self, item, state, tr):
        # optional
        return "nothing happens here"
    
    def hint(self, state):
        # default hint if room forgets to override
        return "no hint here (try 'look' or inspect the file)"