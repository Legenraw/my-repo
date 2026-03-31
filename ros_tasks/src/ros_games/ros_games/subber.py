import rclpy
from rclpy.node import Node
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from ros_msg.msg import VehicleData


class MinimalSubscriber(Node):

    def __init__(self):
        super().__init__('minimal_subscriber')

        self.isListening=False
        self.hasGraphBeenPlotted=True

        self.dist_data=[]
        self.time_data=[]

        self.timer = self.create_timer(1, self.plotTheGraph)
        self.subscription = self.create_subscription(
            VehicleData,
            'topic',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning

    def listener_callback(self, msg):
        if(msg.step==0):
            self.isListening=(self.isListening==False)
            self.hasGraphBeenPlotted=False

        if(self.isListening):
            self.get_logger().info('I heard: "%s"' % msg.step)
            self.dist_data.append(msg.dist)
            self.time_data.append(msg.time)


    def plotTheGraph(self):
        if((not self.isListening) and (not self.hasGraphBeenPlotted)):
            plt.plot(self.time_data,self.dist_data)
            plt.xlabel('Time')
            plt.ylabel('Distance from setpoint')
            plt.show()
            self.hasGraphBeenPlotted=True

def main(args=None):
    rclpy.init(args=args)

    minimal_subscriber = MinimalSubscriber()

    rclpy.spin(minimal_subscriber)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    minimal_subscriber.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
