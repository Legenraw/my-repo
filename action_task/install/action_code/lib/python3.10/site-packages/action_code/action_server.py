import time

import rclpy
from rclpy.action import ActionServer
from rclpy.node import Node

from action_msg.action import ActionInfo


class FibonacciActionServer(Node):

    def __init__(self):
        super().__init__('counter_action_server')
        self._action_server = ActionServer(
            self,
            ActionInfo,
            'counter',
            self.execute_callback)
        self.create_timer(0.1, self.counter_increase)
        self.count=0
        self.current_goal_handle=None
        self.target=0

    def execute_callback(self, goal_handle):
        self.get_logger().info('Goal recieved :)')

        if not self.current_goal_handle==None:
            self.get_logger().info('cancelling previous goal')
            action_result=ActionInfo.Result()
            action_result.final_count=self.count
            self.current_goal_handle.canceled()
            self.current_goal_handle.set_result(action_result)

        self.count=0
        self.current_goal_handle=goal_handle
        self.target=self.current_goal_handle.request.target
        return ActionInfo.Result()

    def counter_increase(self):
        if(self.current_goal_handle==None):
            return
        
        if self.count<self.target:
            self.count+=1
            feedback_msg = ActionInfo.Feedback()
            feedback_msg.current_count = self.count
            self.get_logger().info('Feedback: {0}'.format(feedback_msg.current_count))
            self.current_goal_handle.publish_feedback(feedback_msg)

        else:
            self.get_logger().info("goal has been achieved woooooo")
            final_result = ActionInfo.Result()
            final_result.final_count=self.count
            self.current_goal_handle.succeed()
            self.current_goal_handle.set_result(final_result)
            self.current_goal_handle=None

def main(args=None):
    rclpy.init(args=args)

    fibonacci_action_server = FibonacciActionServer()

    rclpy.spin(fibonacci_action_server)


if __name__ == '__main__':
    main()
