import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

from action_msg.action import ActionInfo


class CounterActionClient(Node):

    def __init__(self):
        super().__init__('counter_action_client')
        self._action_client = ActionClient(self, ActionInfo, 'counter')
        self.current_goal_handle = None
        self.max_num_allowed = 20   

    def send_goal(self, target):
        self.get_logger().info('sending target bro')
        target_goal = ActionInfo.Goal()
        target_goal.target = target
        self._action_client.wait_for_server()
        self._send_goal_future = self._action_client.send_goal_async(target_goal,feedback_callback=self.feedback_callback)
        self._send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()
        self.current_goal_handle = goal_handle
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self.result_callback)

    def feedback_callback(self, feedback_msg):
        print('hi')
        count = feedback_msg.feedback.current_count
        self.get_logger().info(f'Feedback received: {count}')

        if count > self.max_num_allowed:
            self.get_logger().info('khel khatam hai')
            new_target = int(count // 2)
            self.send_goal(new_target)

    def result_callback(self, future):
        result = future.result().result
        self.get_logger().info(str(result.final_count))

def main(args=None):
    rclpy.init(args=args)
    node = CounterActionClient()
    target=int(input("What do you want threshold to be son: "))
    node.send_goal(target) 
    rclpy.spin(node)


if __name__ == '__main__':
    main()