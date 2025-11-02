<<<<<<< HEAD
class Room:
    # this is just the base class others will inherit from
=======
"""Base room class for the escape game.
Other rooms inherit from this and override the methods.
We keep simple defaults so the engine has something to call."""

class Room:
    """Defines the common room interface.
    Each room can handle enter/inspect/use/hint in its own way.
    This keeps everything consistent across rooms."""
>>>>>>> kim

    name = "abstract"

    def enter(self, state):
<<<<<<< HEAD
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
=======
        """Runs when the player has entered the room and uses look.
        We return a short description of the scene."""
        return "Nothing to see here."

    def inspect(self, item, state, tr):
        """Called when the player inspects a file.
        Child classes parse files or show clues and return a message."""
        return "Nothing to inspect here."

    def use(self, item, state, tr):
        """Called when the player uses an item in the room.
        Default does nothing, real rooms override this to act on items if applicable."""
        return "Nothing to use here."
    
    def hint(self, state):
        """Returns a hint for the room.
        Default hint is generic, rooms can override to be helpful."""
        return "No hint here (try 'look' or inspect the file)"
>>>>>>> kim
