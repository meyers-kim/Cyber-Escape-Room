from dataclasses import dataclass, field
from escaperoom.transcript import Transcript
from escaperoom.rooms.base import Room

@dataclass
class GameState:
    # keeps track of everything that happens
    current_room: str = "intro"
    tokens: dict = field(default_factory=dict)
    inventory: set = field(default_factory=set)
    flags: dict = field(default_factory=dict)

    def has_all_tokens(self):
        # 4 tokens in total when we have all the final gate opens
        return len(self.tokens) >= 4


class GameEngine:
    # main engine

    def __init__(self, tr_path="run.txt"):
        self.state = GameState()
        self.tr = Transcript(tr_path)
        self.rooms = {}   # will be filled later with actual rooms

    def register(self, name, room):
        # register a new room by name
        self.rooms[name] = room

    def run(self):
        print("Cyber Escape Room")
        print("type 'help' if you need commands")

        while True:
            cmd = input("> ").strip().lower()
            if not cmd:
                continue

            if cmd in ("quit"):
                print("Goodbye player!")
                break

            self.handle_command(cmd)

        self.tr.close()

    def handle_command(self, cmd):
        parts = cmd.split()
        action = parts[0]
        args = parts[1:]

        if action == "help":
            print("commands: look, move <room>, inspect <item>, inventory, quit")
        elif action == "look":
            room = self.rooms.get(self.state.current_room)
            if room:
                print(room.enter(self.state))
            else:
                print("you are lost somewhere")
        elif action == "move" and args:
            self.move_to(args[0])
        elif action == "inventory":
            print("tokens:", self.state.tokens)
            print("items:", list(self.state.inventory))
        elif action == "inspect" and args:
            room = self.rooms.get(self.state.current_room)
            if not room:
                print("cant inspect here")
                return
            print(room.inspect(args[0], self.state, self.tr))
        else:
            print("unknown command or missing argument")

    def move_to(self, name):
        if name not in self.rooms:
            print("that room does not exist")
            return
        if name == "final" and not self.state.has_all_tokens():
            print("you need all tokens before entering the final gate!")
            return
        self.state.current_room = name
        print(f"you move to the {name} room")