from escaperoom.engine import GameEngine
from escaperoom.rooms.intro import IntroRoom

def main():
    engine = GameEngine()
    # only intro room for now others will be added later
    engine.register("intro", IntroRoom())
    engine.state.current_room = "intro"
    engine.run()

if __name__ == "__main__":
    main()