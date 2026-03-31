#import sys; sys.path.append("~/freshie/src")
from src.games.game4_ml_recognition import Game4MLRecognition
from src.controllers.pid_controller_game1 import PIDControllerGame1

def main():
    """Entry point for the Submarine Training Arena."""
    game = Game4MLRecognition()
    controller = PIDControllerGame1(game.config)
    game.set_controller(controller)
    game.run()


if __name__ == "__main__":
    main()
