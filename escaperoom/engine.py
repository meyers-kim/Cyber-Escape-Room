"""Game engine for the CLI.
Runs the REPL, routes commands to rooms, and saves/loads state."""

import json
import os

from dataclasses import dataclass, field, asdict
from escaperoom.transcript import Transcript
from escaperoom.rooms.base import Room
from escaperoom.rooms.soc import SocRoom
from escaperoom.rooms.dns import DnsRoom
from escaperoom.rooms.vault import VaultRoom
from escaperoom.rooms.malware import MalwareRoom
from escaperoom.rooms.final import FinalGateRoom

@dataclass
class GameState:
    """Holds the current room and tokens.
    This is what we save and load back."""
    current_room: str = "intro"
    tokens: dict = field(default_factory=dict)
    flags: dict = field(default_factory=dict)

    def has_all_tokens(self):
        """Check if the player has 4 tokens.
        When true, the final gate can be entered."""
        return len(self.tokens) >= 4
    
    def to_dict(self):
        """Convert the state to a plain dict.
        Used by json.dump when saving."""
        return asdict(self)

    @classmethod
    def from_dict(cls, d):
        """Create a GameState from a dict.
        Fills defaults if keys are missing."""
        obj = cls()
        obj.current_room = d.get("current_room", "intro")
        obj.tokens = dict(d.get("tokens", {}))
        obj.flags = dict(d.get("flags", {}))
        return obj


class GameEngine:
    """Main loop and command router.
    Reads input, calls room methods, and writes the transcript."""
    
    def __init__(self, tr_path="run.txt"):
        """Create a fresh game with a transcript.
        Rooms are registered later by the entry script."""
        self.state = GameState()
        self.tr = Transcript(tr_path)
        self.rooms: dict[str, Room] = {} 
        
    def register(self, name, room):
        # register a new room by name
        self.rooms[name] = room

    def run(self):
        """Text REPL for the game.
        Reads commands until the player quits."""
        print("=== Cyber Escape Room (Group8) ===")
        print(
            "Welcome to our Cyber Escape Room! Move between rooms, inspect and solve one file per room,\n"
            "collect four tokens to open the final gate to escape. Good luck!\n"
        )
        print("Type 'help' for commands\n")

        while True:
            try:
                cmd = input("> ").strip()
            except (EOFError, KeyboardInterrupt):
                if self.confirm_quit():
                    break
                else:
                    print("\nokay, lets continue!\n")
                    continue

            if not cmd:
                continue

            if cmd == "quit":
                if self.confirm_quit():
                    break
                else:
                    print("\nokay, let's continue!\n")
                    continue

            self.handle_command(cmd)

        try:
            self.tr.close()
        except Exception:
            pass
        
    def confirm_quit(self):
        """Ask the player if they really want to quit.
        Shows tokens and a small tip about saving."""
        tokens_text = self._format_tokens_for_quit()
        print("\nAre you sure you want to quit the Cyber Escape Room?")
        if tokens_text:
            print(f"You currently hold the following token(s): {tokens_text}")
        else:
            print("You currently dont hold any tokens.")
        print(
            "Tip: you can still 'save <file>' or 'load <file>' before quitting."
            "If you want to save your progress, or if you want to continue with an other save file."
        )

        choice = input("Type 'yes' to quit, or anything else to stay: ").strip().lower()
        if choice == "yes":
            print("Thank you for playing, we hope you come back soon to finish your journey.")
            return True
        return False
    
    def _format_tokens_for_quit(self):
        """Turn the tokens dict into 'KEY=VAL, KEY=VAL'.
        Returns empty string if no tokens yet."""
        if not self.state.tokens:
            return ""
        parts = [f"{k}={v}" for k, v in sorted(self.state.tokens.items())]
        return ", ".join(parts)

    def handle_command(self, cmd):
        """Parse one command line and run the action."""
        parts = cmd.split()
        action = parts[0].lower()
        args = parts[1:]

        if action == "help":
            print(
                "commands:\n"
                "  look            - describe the current room and which item is visible to you\n"
                "  move <room>     - go to another room (soc, dns, vault, malware, final)\n"
                "  inspect <item>  - check or read a file in the room for clues and to solve it\n"
                "  use <item>      - try using something, like opening the final gate\n"
                "  hint            - get a small hint for what to do next\n"
                "  inventory       - show which tokens you have collected\n"
                "  save <file>     - save your current game progress\n"
                "  load <file>     - load a previously saved game file\n"
                "  quit            - exit the game"
            )

        elif action == "look":
            room = self.rooms.get(self.state.current_room)
            if room:
                print(room.enter(self.state) + "\n")
            else:
                print("You are lost somewhere")

        elif action == "move" and args:
            self.move_to(args[0])
            print("")

        elif action == "inventory":
            print("tokens:", self.state.tokens)

        elif action == "inspect" and args:
            room = self.rooms.get(self.state.current_room)
            if not room:
                print("You cant inspect here")
                return
            print(room.inspect(args[0], self.state, self.tr))

        elif action == "use" and args:
            room = self.rooms.get(self.state.current_room)
            if not room:
                print("Nowhere to use things")
                return
            print(room.use(args[0], self.state, self.tr))
        
        elif action == "hint":
            room = self.rooms.get(self.state.current_room)
            if room:
                print(room.hint(self.state) + "\n")
            else:
                print("Here are no hints.\n")

        elif action == "save" and args:
            self._save_game(args[0])
            print("")

        elif action == "load" and args:
            self._load_game(args[0])
            print("")

        else:
            print("Unknown command or missing argument!")

    def move_to(self, name):
        """Move the player to a different room.
        Blocks the final room until all tokens are collected."""
        name = name.lower()
        if name not in self.rooms:
            print("That room does not exist, please try another one.")
            return
        if name == "final" and not self.state.has_all_tokens():
            print("You need to collect all 4 tokens before entering the final gate!")
            return
        self.state.current_room = name
        print(f"You just moved to the {name} room, it might be good to have a look!")
        
        
    def _save_game(self, path):
        """Save the current gameState to JSON.
        Creates a 'saves' folder if no path is given."""
        try:
            dirname = os.path.dirname(path)
            basename = os.path.basename(path) or "save"
            if not dirname:
                save_dir = "saves"
                if not os.path.exists(save_dir):
                    os.makedirs(save_dir, exist_ok=True)
                if not basename.lower().endswith(".json"):
                    basename = basename + ".json"
                path = os.path.join(save_dir, basename)
            else:
                # create folder
                if dirname and not os.path.exists(dirname):
                    os.makedirs(dirname, exist_ok=True)

            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.state.to_dict(), f, ensure_ascii=False, indent=2)
            print(f"[Game] Progress saved: {path}")
        except Exception as e:
            print(f"[Game] Save failed: {e}")

    def _load_game(self, path):
        """Load GameState from a JSON file.
        Checks both the given path and the default 'saves' folder."""
        try:
            # if user gives a name look for it
            dirname = os.path.dirname(path)
            basename = os.path.basename(path)
            if not dirname:
                try_path = os.path.join("saves", basename if basename else path)
                if not try_path.lower().endswith(".json"):
                    try_path = try_path + ".json"
            else:
                try_path = path

            with open(try_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.state = GameState.from_dict(data)
            if self.state.current_room not in self.rooms:
                self.state.current_room = "intro"
            print(f"[Game] Progress loaded: {try_path}")
        except FileNotFoundError:
            print("[Game] No such save file")
        except Exception as e:
            print(f"[Game] Load failed: {e}")