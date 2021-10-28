#!/usr/bin/env python
import rospy as rp
from autoware_msgs.msg import ControlCommandStamped
from std_msgs.msg import Float32


def input_callback(data,params):
    params[0][params[1]]=data.data





rp.init_node("CommandConverter")
control_topic=rp.get_param("control_convert_topic")
wheel_control=rp.get_param("wheel_control_topics") #dictionary "side":value
wheel_values={"left":0,"right":0}
print wheel_control
left_sub=rp.Subscriber(wheel_control["left"],Float32,input_callback,[wheel_values,"left"],queue_size=10)
right_sub=rp.Subscriber(wheel_control["right"],Float32,input_callback,[wheel_values,"right"],queue_size=10)


rate=rp.Rate(60.0)


print control_topic

publisher = rp.Publisher(control_topic,ControlCommandStamped,queue_size=10)
while not rp.is_shutdown():
    msg=ControlCommandStamped()
    msg.header.stamp=rp.get_rostime()
    msg.cmd.linear_velocity=wheel_values["right"]
    msg.cmd.steering_angle = wheel_values["left"]
    publisher.publish(msg)
    rate.sleep()
    pass
msg=ControlCommandStamped()
publisher.publish(msg)
rate.sleep()