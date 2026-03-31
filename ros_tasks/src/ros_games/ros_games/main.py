#import os
#import sys; sys.path.append(os.path.expanduser("/home/legenraw/freshie/src"))
import threading
from ros_games.src_pkg.games.game2_obstacle_avoidance import Game2ObstacleAvoidance
from ros_games.src_pkg.controllers.pid_controller_game1 import PIDControllerGame1
import rclpy
from rclpy.node import Node
from ros_msg.srv import Reset

class TheGame(Node):

    def __init__(self):
        super().__init__('the_game')

        self.game = Game2ObstacleAvoidance()
        self.controller = PIDControllerGame1(self.game.config)
        self.game.set_controller(self.controller)

        self.srv = self.create_service(
            Reset,
            'num_of_obstacles',
            self.reset_the_game_yo
        )

    def reset_the_game_yo(self, request, response):
        response.obstacle_number = request.obstacle_num
        self.game.reset_game()
        self.get_logger().info('service done yo')
        return response


def main():
    #rclpy.init()

    node = TheGame()

    # spin ROS in background thread
    ros_thread = threading.Thread(target=rclpy.spin, args=(node,))
    ros_thread.daemon = True
    ros_thread.start()

    # run game loop in main thread
    node.game.run()

    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
