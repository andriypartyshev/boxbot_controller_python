#!/usr/bin/env python
from sensor_msgs.msg import Joy

class Joystick:

    button_layout={"A":0,
                   "B":1,
                   "X":2,
                   "Y":3,
                   "LB":4,
                   "RB":5,
                   "LS":9,
                   "RS":10}
    axis_layout={"LeftT":2,
                 "RightT":5,
                 "LeftH":0,
                 "LeftV":1,
                 "RightH":3,
                 "RightV":4,
                 "DpadH":6,
                 "DpadV":7}

    def __init__(self, j_data=Joy()):
        self.joy_data = j_data
        pass

    def getDpad(self,direction):
        if (direction =="up"):
            return True if self.getAxis("DpadV")>0.9 else False
        if (direction =="down"):
            return True if self.getAxis("DpadV")<-0.9 else False
        if (direction =="left"):
            return True if self.getAxis("DpadH")<-0.9 else False
        if (direction =="right"):
            return True if self.getAxis("DpadH")>0.9 else False

        return False

    def getButton(self,key):
        try:
            return self.joy_data.buttons[self.button_layout[key]]
        except:
            # print "No Button Pressed"
            return None

    def getAxis(self,key):

        try:
            return self.joy_data.axes[self.axis_layout[key]]
        except:
            # print "No Button Pressed"
            return -2

    def updateValue(self, j_data):

        self.joy_data=j_data

    def getTriggerAxis(self):

        try:
            return (abs(self.getAxis("RightT")+1)/2)-(abs(self.getAxis("LeftT")+1)/2) if (abs(self.getAxis("RightT"))<1.1 and  abs(self.getAxis("LeftT"))<1.1) else 0
        except:
            return 0

    def __str__(self):

        return self.joy_data.axes.__str__()

    def __getitem__(self, item):

        if item in self.button_layout:
            return self.getButton(item)
        elif item in self.axis_layout:
            return self.getAxis(item) if abs(self.getAxis(item))<1.2 else 0
        elif item == "Trigger":
            return self.getTriggerAxis()
        else:
            return None
