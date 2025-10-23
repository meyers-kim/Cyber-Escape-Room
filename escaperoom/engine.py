from dataclasses import dataclass, field, asdict
from escaperoom.transcript import Transcript
from escaperoom.rooms.base import Room
from escaperoom.rooms.soc import SocRoom
from escaperoom.rooms.dns import DnsRoom
from escaperoom.rooms.vault import VaultRoom
from escaperoom.rooms.malware import MalwareRoom
from escaperoom.rooms.final import FinalGateRoom

import json
import os

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
    
    # json cant handle set directly so i convert
    def to_dict(self):
        d = asdict(self)
        d["inventory"] = list(self.inventory)
        return d

    @classmethod
    def from_dict(cls, d):
        obj = cls()
        obj.current_room = d.get("current_room", "intro")
        obj.tokens = dict(d.get("tokens", {}))
        obj.inventory = set(d.get("inventory", []))
        obj.flags = dict(d.get("flags", {}))
        return obj


class GameEngine:
    # main engine

    def __init__(self, tr_path="run.txt"):
        self.state = GameState()
        self.tr = Transcript(tr_path)
        self.rooms: dict[str, Room] = {} 
    def register(self, name, room):
        # register a new room by name
        self.rooms[name] = room

    def run(self):
        print("Cyber Escape Room")
        print("type 'help' if you need commands")

        while True:
            try:
                cmd = input("> ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nbye")
                break

            if not cmd:
                continue

            low = cmd.lower()
            if low in ("quit", "exit"):
                print("Goodbye player!")
                break

            self.handle_command(cmd)

        self.tr.close()

    def handle_command(self, cmd):
        parts = cmd.split()
        action = parts[0].lower()
        args = parts[1:]

        if action == "help":
            print("commands: look, move <room>, inspect <item>, use <item>, inventory, save <file>, load <file>, quit")

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

        elif action == "use" and args:
            room = self.rooms.get(self.state.current_room)
            if not room:
                print("nowhere to use things")
                return
            print(room.use(args[0], self.state, self.tr))

        elif action == "save" and args:
            self._save_game(args[0])

        elif action == "load" and args:
            self._load_game(args[0])

        else:
            print("unknown command or missing argument")

    def move_to(self, name):
        name = name.lower()
        if name not in self.rooms:
            print("that room does not exist")
            return
        if name == "final" and not self.state.has_all_tokens():
            print("you need all tokens before entering the final gate!")
            return
        self.state.current_room = name
        print(f"you move to the {name} room")
        
        
    def _save_game(self, path):
        # save just the state the transcript keeps going normally
        try:
            folder = os.path.dirname(path)
            if folder and not os.path.exists(folder):
                os.makedirs(folder, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.state.to_dict(), f, ensure_ascii=False, indent=2)
            print("[Game] Progress saved")
        except Exception as e:
            print(f"[Game] save failed: {e}")

    def _load_game(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.state = GameState.from_dict(data)
            if self.state.current_room not in self.rooms:
                self.state.current_room = "intro"
            print("[Game] Progress loaded")
        except FileNotFoundError:
            print("[Game] no such save file")
        except Exception as e:
            print(f"[Game] load failed: {e}")    