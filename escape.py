"""CLI entry point for the game.
Parses arguments, registers all rooms, and starts the main game loop.
"""

import argparse
from escaperoom.engine import GameEngine
from escaperoom.rooms import (
    IntroRoom, SocRoom, DnsRoom, VaultRoom, MalwareRoom, FinalGateRoom
)

def main():
    """Starts the game.
    Parses optional arguments for start room, transcript file, and save file.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", default="intro", help="room to start in (intro/soc/dns/vault/malware/final)")
    parser.add_argument("--transcript", default="run.txt", help="file where transcript will be saved")
    parser.add_argument("--load", default="", help="optional: load a save file before starting")
    args = parser.parse_args()

    # create the main game engine and  pass transcript path
    engine = GameEngine(tr_path=args.transcript)

    # register all the rooms so that we can move 
    engine.register("intro", IntroRoom())
    engine.register("soc", SocRoom())
    engine.register("dns", DnsRoom())
    engine.register("vault", VaultRoom())
    engine.register("malware", MalwareRoom())
    engine.register("final", FinalGateRoom())

    if args.load:
        try:
            engine._load_game(args.load)
            print("")
        except Exception:
            # ignore errors here
            pass

    # decide start room and if nothing is selected the player starts in the intro room
    desired = (args.start or "intro").lower()
    if desired not in engine.rooms:
        desired = "intro"

    # if the player tries to start in final but doesnt have tokens the intro room will be selected
    if desired == "final" and not engine.state.has_all_tokens():
        print("You can't start in the final room without all 4 tokens. You will be send to the intro room instead.\n")
        desired = "intro"

    engine.state.current_room = desired
    engine.run()

if __name__ == "__main__":
    main()