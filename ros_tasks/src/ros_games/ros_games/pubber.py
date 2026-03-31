import rclpy
import re
from rclpy.node import Node
from ros_msg.msg import VehicleData
import sys

class Data_parser_pubber(Node):

    def __init__(self,given_file):
        super().__init__('minimal_publisher')

        Tfile=given_file
        self.parsed_ep_data=self.parse_file(Tfile)
        self.publisher_ = self.create_publisher(VehicleData, 'topic', 10)
        timer_period = 0.001  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.i=0

    def timer_callback(self):
        msg = VehicleData()
        if(self.i==len(self.parsed_ep_data)):
            self.get_logger().info('And thats it  >:) ')
            self.publisher_.publish(msg)
            rclpy.shutdown()
        else:
            msg.step=int(self.parsed_ep_data[self.i]['step'])
            msg.time=float(self.parsed_ep_data[self.i]['time'])
            msg.pos_x=float(self.parsed_ep_data[self.i]['posx'])
            msg.pos_y=float(self.parsed_ep_data[self.i]['posy'])
            msg.vel_x=float(self.parsed_ep_data[self.i]['velx'])
            msg.vel_y=float(self.parsed_ep_data[self.i]['vely'])
            msg.orient=float(self.parsed_ep_data[self.i]['orient'])
            msg.ang_vel=float(self.parsed_ep_data[self.i]['angvel'])
            msg.speed=float(self.parsed_ep_data[self.i]['speed'])
            msg.dist=float(self.parsed_ep_data[self.i]['dist'])
            msg.is_colliding=self.parsed_ep_data[self.i]['iscolliding']=='True'
            msg.nearest_obstacle=float(self.parsed_ep_data[self.i]['nearest'])
            self.get_logger().info('Publishing: "%s"' % self.parsed_ep_data[self.i]['step'])
            self.publisher_.publish(msg)
        self.i+=1

    def parse_file(self,file):
        parsed_data=[]
        pattern=r'Step (?P<step>.*?) \| Time: (?P<time>.*?)s \| Pos: \((?P<posx>.*?), (?P<posy>.*?)\) \| Vel: \((?P<velx>.*?), (?P<vely>.*?)\) \| Orient: (?P<orient>.*?) rad \| AngVel: (?P<angvel>.*?) \| Speed: (?P<speed>.*?) \| DistToTarget: (?P<dist>.*?) \| Colliding: (?P<iscolliding>.*?) \| NearestObstacle: (?P<nearest>.*)'
        for line in file:
            parse=re.search(pattern,line)
            if parse:
                parsed_data.append(parse.groupdict())
        return parsed_data

def main(args=None):
    rclpy.init(args=args)
    with open("logs/episode_002/telemetry.txt") as openedFile:
        parsed_data_publisher = Data_parser_pubber(openedFile)

    rclpy.spin(parsed_data_publisher)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    parsed_data_publisher.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
