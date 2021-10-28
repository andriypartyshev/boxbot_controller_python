#!/usr/bin/env python
true=True
false=False
'''
#include <ros/ros.h>

#include <std_msgs/Float32.h>
#include <std_msgs/Bool.h>
#include <std_msgs/Empty.h>
#include <std_msgs/String.h>
#include <sensor_msgs/Joy.h>
#include <sensor_msgs/LaserScan.h>
#include <autoware_msgs/ControlCommandStamped.h>
#include <iseauto_msgs/VehicleControllerMode.h>
#include <iseauto_msgs/VehicleControllerModeStamped.h>
#include <iseauto_msgs/VehicleControllerParamsStamped.h>
#include <geometry_msgs/TwistStamped.h>
#include <actionlib_msgs/GoalStatusArray.h>

#include <actionlib_msgs/GoalStatus.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>
'''
import rospy
import sensor_msgs.msg

from iseauto_msgs.msg import VehicleControllerMode
from autoware_msgs.msg import ControlCommand
from PyJoyDecoder import Joystick
from PyDriveTrain import Drive
from std_msgs.msg import Float32,Bool
def feedback_callback(data,params):
    params[0][params[1]]=data.data

cam_takeover_ready=False

def cam_takeover_callback(data):
    global cam_takeover_ready
    cam_takeover_ready=data.data


control_toggle={
        "searching":False,
        "mode":"safe",
        "dead_man":False,
        "shutdown":false

    }

def joy_callback(data,joy):
    if joy is not None:
        joy.updateValue(data)

    else:
        joy=Joystick(data)
    # rospy.loginfo(joy)

    pass

oldmode=""
def update_joy(joy):
    control_toggle["dead_man"] = (joy["LB"] == 1) and (joy["RB"] == 1)
    if joy["A"] == 1:
        control_toggle["mode"] = "auto"
    elif joy["X"] == 1:
        control_toggle["mode"] = "manual"
    elif joy["B"] == 1:
        control_toggle["mode"] = "safe"
    if joy["Y"]:
        control_toggle["shutdown"]=true

    if joy.getDpad("left"):
        control_toggle["searching"]=false
    elif joy.getDpad("right"):
        control_toggle["searching"] = True





def runtime():
    global cam_takeover_ready
    rospy.init_node('Joy_Decoder')
    wheel_control = rospy.get_param("wheel_control_topics")
    auto_control_input = rospy.get_param("auto_control_topics")
    wheel_feedback = rospy.get_param("wheel_feedback_topics")# dictionary "side":value
    control_multipliers=rospy.get_param("control_multipliers")
    cam_takeover_status_topic = rospy.get_param("cam_takeover_status_topic")
    jj=Joystick()
    joy_sub=rospy.Subscriber("/joy",sensor_msgs.msg.Joy,joy_callback,jj)
    rate=rospy.Rate(30.0)
    pub_left = rospy.Publisher(wheel_control["left"],Float32, queue_size=10)
    pub_right = rospy.Publisher(wheel_control["right"], Float32, queue_size=10)
    wheel_velocities={"left":0,"right":0}
    auto_control = {"linear": 0, "angular": 0}
    # control_multipliers = {"auto":{"linear": 0, "angular": 0},"manual":{"linear": 0, "angular": 0}}
    left_sub = rospy.Subscriber(wheel_feedback["left"], Float32, feedback_callback, [wheel_velocities, "left"], queue_size=10)
    right_sub = rospy.Subscriber(wheel_feedback["right"], Float32, feedback_callback, [wheel_velocities, "right"], queue_size=10)
    cam_takeover_status_sub = rospy.Subscriber(cam_takeover_status_topic, Bool, cam_takeover_callback,queue_size=10)

    auto_linear = rospy.Subscriber(auto_control_input["linear"], Float32, feedback_callback, [auto_control, "linear"],
                                queue_size=10)
    auto_angular = rospy.Subscriber(auto_control_input["angular"], Float32, feedback_callback, [auto_control, "angular"],
                                 queue_size=10)


    _drive=Drive(3,0,0,-3000,3000,300)





    while not rospy.is_shutdown() and not control_toggle["shutdown"]:


        left=0
        right=0
        if control_toggle["mode"]=="manual":
            # rospy.loginfo(wheel_velocities)
            print ("manual")


            if control_toggle["dead_man"]:
                print ("active")
                left, right = _drive.update(-jj["Trigger"] * control_multipliers["manual"]["linear"],
                                            (jj["RightH"]+jj["LeftH"]) * control_multipliers["manual"]["angular"],
                                            wheel_velocities["left"],
                                            wheel_velocities["right"])
               # ,jj["LeftV"] * control_multipliers["manual"]["linear"],jj["RightH"] * control_multipliers["manual"]["angular"],wheel_velocities["left"],wheel_velocities["right"]





        elif control_toggle["mode"]== "auto":
            # rospy.loginfo(wheel_velocities)

            print "auto"
            left,right=_drive.update(auto_control["linear"]*control_multipliers["auto"]["linear"],
                                     auto_control["angular"]*control_multipliers["auto"]["angular"],
                                     wheel_velocities["left"],
                                     wheel_velocities["right"])


        else:
            print "safe"

            _drive.clear()

        print control_toggle["searching"], cam_takeover_ready
        if control_toggle["searching"]:
            if cam_takeover_ready:
                control_toggle["mode"] = "auto"
                cam_takeover_ready=false

        # print left, right
        pub_left.publish(left)
        pub_right.publish(right)

        update_joy(jj)
        rate.sleep()
        print "----------"

    pass
    pub_left.publish(0)
    pub_right.publish(0)
    rospy.signal_shutdown("Clean")
    rate.sleep()
    return


# if __name__ == '__main__':
runtime()
