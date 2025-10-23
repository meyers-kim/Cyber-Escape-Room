import argparse
from escaperoom.engine import GameEngine
from escaperoom.rooms import (
    IntroRoom, SocRoom, DnsRoom, VaultRoom, MalwareRoom, FinalGateRoom
)

def main():
    # argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", default="intro", help="room to start in (intro/soc/dns/vault/malware/final)")
    parser.add_argument("--transcript", default="run.txt", help="file where transcript will be saved")
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

    # pick which room to start in
    start_room = args.start.lower()
    if start_room not in engine.rooms:
        print(f"[warn] room '{start_room}' not found, using intro instead")
        start_room = "intro"
    engine.state.current_room = start_room

    # small info lines so i know whats going on
    print(f"[Game] start room -> {start_room}")
    print(f"[Game] transcript -> {args.transcript}")
    print("type 'help' once the game starts if you forget the commands")

    engine.run()

if __name__ == "__main__":
    main()