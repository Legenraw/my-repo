import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from games.game1_target_reaching import Game1TargetReaching
from config import Config
from controllers.pid_controller_game1 import PIDControllerGame1

config = Config()
config.headless = True
config.max_steps = 3000
config.max_time = 60.0
config.logging['enabled'] = False
config.game1_config['success_radius'] = 30
config.game1_config['auto_reset'] = False

game = Game1TargetReaching(config)
controller = PIDControllerGame1(config)
game.set_controller(controller)
game.run()

print(f"Success: {game.episode_success}")
print(f"Steps: {game.current_step}, Time: {game.current_time:.2f}s")
if game.target:
    print(f"Distance: {game.target.distance_to(game.vehicle.position):.1f}")

