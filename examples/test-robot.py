#!/usr/bin/env python3
##############################################
# The MIT License (MIT)
# Copyright (c) 2018 Kevin Walchko
# see LICENSE for full details
##############################################

from __future__ import print_function
from __future__ import division
from multiped import Engine
# from multiped import DiscreteRippleGait
from multiped import Kinematics4
from pyservos import AX12
import time
from math import pi, sqrt
from enum import IntFlag
import platform
import sys
from Gait2 import Discrete
from plotting import rplot, rplot2, plot_body_frame
from pprint import pprint

"""
need:

      cmd      3d pts      DH angles        servo packet
robot --> gait -----> legs --------> engine -----------> servos

robot:
- sensors
- AI
- Holds:
    - kinematics
    - gait
    - engine
- knows:
    - command
    - 3d points
    - dh angles

Kinematics
- init: link lengths
- F/I Kinematics

Gait:
- init: neutral pos
- step sequence

Engine:
- init: servoType, current pos, servoOffsets, serial port
- serial connection
- servo protocol (ax12, xl430, rcservo, etc)
- DH2ServoAngles

Issues:
--------
- gait should drive speed, right now kinematics sets all movements the same
- transition from N->A and A->N
    - which class knows what
    - need to shift body CM
"""


class RobotTest(object):
    def __init__(self):
        bcm_pin = None
        if True:  # manual override for testing - don't actually talk to servos
            ser = 'fake'
        elif platform.system() == 'Darwin':
            ser = '/dev/tty.usbserial-A506BOT5'
        elif platform.system() == 'Linux':
            ser = '/dev/serial0'
            bcm_pin = 17
        else:
            raise Exception('Your OS is not supported')

        data = {
            # [ length, (limit_angles), offset_angle] - units:mm or degrees
            # 'coxa':   [52, [-90, 90], 150],
            # 'femur':  [90, [-90, 90], 123],   # fixme
            # 'tibia':  [89, [-90, 120], 194],  # fixme
            # 'tarsus': [90, [-90, 90], 167],
            'numLegs': 4,          # helps?
            'numServosPerLeg': 4,  # helps?
            'coxa':   [52, 150],   # length [mm], offset [deg]
            'femur':  [90, 123],
            'tibia':  [89, 194],
            'tarsus': [90, 167],

            'sit': (80, 0, 1,),     # foot position [mm]
            'stand': (120, 0, -70), # foot position [mm]

            # engine
            # types: 1:ax12 2:xl320 4:xl430
            'servoType': 1,  # switch to IntFlags
            'serialPort': ser,
            'bcm_pin': bcm_pin
        }

        self.positions = {
            'stand': data['stand'],
            'sit': data['sit']
        }

        self.kinematics = Kinematics4(data)
        self.gait = Discrete(self.positions['stand'])

        self.engine = Engine(data, AX12)

        # where are the feet currently ... angles?
        self.currentAngles = {}  # DH angles
        dh_angles = self.engine.getCurrentAngles()
        self.currentAngles = dh_angles  # value??
        # where are the feet currently ... (x,y,z)?
        self.currentFeet = {}  # (x,y,z)
        for i, angles in dh_angles.items():
            # print(angles)
            self.currentFeet[i] = list(self.kinematics.forward(*angles))
        print("current feet",self.currentFeet)
        self.stand(self.currentFeet)

    def __del__(self):
        current = self.getFeetPosition()
        self.sit(current)

    def getFeetPosition(self):
        """
        return {0:(x,y,z), 1:(x,y,z), ...}
        """
        dh_angles = self.engine.getCurrentAngles()
        currentFeet = {}  # (x,y,z)
        for i, angles in dh_angles.items():
            # print(angles)
            currentFeet[i] = list(self.kinematics.forward(*angles))
        print("current feet",currentFeet)
        return currentFeet

    def walk(self):
        print(" <<<==========  Walk  ==========>>>")
        # predefined walking path
        # x, y, rotation
        CmdState = IntFlag('CmdState', 'linear rotational neutral')
        state = CmdState.neutral
        path = [
            [1.0, 0.0, 0],
            # [1.0, 0, 0],
            # [1.0, 0, 0],
            # [1.0, 0, 0],
            # [1.0, 0, 0],
            # [1.0, 0, 0],
            # [1.0, 0, 0],
            # [1.0, 0, 0],
            # [1.0, 0, 0],
            # [1.0, 0, 0],
            # [0, 0, pi/4],
            # [0, 0, pi/4],
            # [0, 0, pi/4],
            # [0, 0, -pi/4],
            # [0, 0, -pi/4],
            # [0, 0, -pi/4],
            # [-1.0, 0, 0],
            # [-1.0, 0, 0],
            # [-1.0, 0, 0],
            # [-1.0, 0, 0],
            # [-1.0, 0, 0],
            # [-1.0, 0, 0],
            # [-1.0, 0, 0],
            # [-1.0, 0, 0],
            # [-1.0, 0, 0],
            # [-1.0, 0, 0],
        ]

        # cp = self.getFeetPosition()
        self.toGait()
        return

        for cmd in path:
            # if cmd[2] == 0:
            #     if state == CmdState.neutral or state == CmdState.rotational:
            #         self.toGait()
            #         state = CmdState.linear
            # else:
            #     if state == CmdState.linear:
            #         self.toNeutral()
            #         state = CmdState.rotational

            pts = self.gait.command(cmd)        # get 3d feet points

            # # save 3d points
            # for i in pts.keys():
            #     self.currentFeet[i] = pts[i][-1]
            #
            plot_body_frame(pts,1)
            #
            # # pts = (x,y,z) for each leg for the whole cycle
            # # speed = max speed seen by any joint, most likely it will be lower
            angles_speeds = self.kinematics.generateDHAngles(pts, 200)  # get servo angles

            # rplot2(angles_speeds[0])

            # only move 1 leg, remove others from commands
            # if False:
            #     angles_speeds.pop(2)
            #     angles_speeds.pop(1)
            #     angles_speeds.pop(3)

            self.engine.moveLegsGait4(angles_speeds)  # send commands to servos

        # self.toNeutral()

    def step(self, leg, p1, p2, lift):
        """
        Pick the foot up and set it down
        leg - which leg number 0-3
        p1 - start (x,y,z)
        p2 - stop (x,y,z)
        lift - how high to lift the foot
        """
        pass

    def toNeutral(self, speed=100):
        return

    def toGait(self, speed=100):
        curr = self.getFeetPosition()
        # fin = list(self.positions['stand'])
        fin = {
            0: self.gait.steps[0],
            1: self.gait.steps2[0],
            2: self.gait.steps2[0],
            3: self.gait.steps[0],
        }
        # self.shift(curr, fin, speed)

        steps = {0:[],1:[],2:[],3:[]}
        for leg in range(4):
            steps[leg].append(curr[leg])
        for leg in range(4):
            c = steps[leg][0].copy()
            c[2] = 0
            steps[leg].append(c)
            f = list(fin[leg])
            f[2] = 0
            steps[leg].append(f)
            steps[leg].append(fin[leg])

        pprint('steps', steps)

        plot_body_frame(steps,1)

        angles_speeds = self.kinematics.generateDHAngles(steps, speed)
        self.engine.moveLegsGait4(angles_speeds)
        time.sleep(1)

    def shift(self, curr, final, speed):
        """
        Puts legs into a sitting position
        """
        print(" <<<========== Walk ==========>>> ")
        # time.sleep(1)
        # feet = {}
        # for leg in range(4):
        #     print('d', self.engine.last_move[leg])  # these are servo angles!!!!
        #     x,y,z,s = self.engine.last_move[leg]
        #     feet[leg] = ((x,y,0),(80, 0, 1),)  # foot position in mm

        # pt = ((self.gait.rest[0],0,0,),(80, 0, 1,),)  # foot position in mm

        # find = list(self.positions['stand'])
        find = final.copy()
        finu = find.copy()
        finu[2] = 0

        lift = curr.copy()
        lift[0][2] = 0
        lift[1][2] = 0
        lift[2][2] = 0
        lift[3][2] = 0

        # feet = {
        #     0: (lift[0], finu, find,),
        #     1: (lift[1], finu, find,),
        #     2: (lift[2], finu, find,),
        #     3: (lift[3], finu, find,),
        # }
        def xyMag(a, b):
            return sqrt((b[0]-a[0])**2 + (b[1]-a[1])**2)

        def over(a, o):
            # print('a', a)
            # print('o', o)
            t = [0]*3
            t[0] = a[0] + o[0]
            t[1] = a[1] + o[1]
            t[2] = a[2]
            return t

        off = 20
        diff = 5
        offset = {
            0: ((off,0,), (0,-off,), (-off,0,), (0,off,)),
            1: ((0,off,), (off,0,), (0,-off,), (-off,0,)),
            2: ((-off,0,), (0,off,), (off,0,), (0,-off,)),
            3: ((0,-off,), (-off,0,), (0,off,), (off, 0,))
        }
        feet = {0:[], 1:[], 2:[], 3:[]}
        for leg in range(4):
            if (diff < xyMag(find[leg], curr[leg])):
                for ft in range(4):
                    s = over(curr[leg], offset[leg][ft])
                    feet[ft].append(s.copy())
                    s[2] = 0
                    feet[ft].append(s)
                    feet[ft].append(finu)
                    feet[ft].append(find)

        angles_speeds = self.kinematics.generateDHAngles(feet, speed)
        self.engine.moveLegsGait4(angles_speeds)
        time.sleep(1)


    def sit(self, curr, speed=100):
        """
        Puts legs into a sitting position
        """
        print(" <<<========== Sit ==========>>> ")
        # time.sleep(1)
        # feet = {}
        # for leg in range(4):
        #     print('d', self.engine.last_move[leg])  # these are servo angles!!!!
        #     x,y,z,s = self.engine.last_move[leg]
        #     feet[leg] = ((x,y,0),(80, 0, 1),)  # foot position in mm

        # pt = ((self.gait.rest[0],0,0,),(80, 0, 1,),)  # foot position in mm

        fin = self.positions['sit']

        curr[0][2] = 0
        curr[1][2] = 0
        curr[2][2] = 0
        curr[3][2] = 0

        feet = {
            0: (curr[0], fin,),
            1: (curr[1], fin,),
            2: (curr[2], fin,),
            3: (curr[3], fin,),
        }
        angles_speeds = self.kinematics.generateDHAngles(feet, speed)
        self.engine.moveLegsGait4(angles_speeds)
        time.sleep(2)

    def stand(self, curr, speed=100):
        """
        Puts legs into a standing position
        """
        print(" <<<========== Stand ==========>>> ")
        # angles = self.positions['stand']
        # # ans = [x for x in self.positions['stand']]
        # ans = self.positions['stand']
        # feet = {
        #     0: [ans+[speed]],
        #     1: [ans+[speed]],
        #     2: [ans+[speed]],
        #     3: [ans+[speed]],
        # }
        #
        # print(feet)
        #
        # self.engine.moveLegsGait3(feet)
        # time.sleep(1)
        # pt = ((130, 0, -70),)  # foot position in mm
        # pt = (self.gait.rest,)
        fin = self.positions['stand']

        curr[0][2] = 0
        curr[1][2] = 0
        curr[2][2] = 0
        curr[3][2] = 0
        feet = {
            0: (curr[0], fin,),
            1: (curr[1], fin,),
            2: (curr[2], fin,),
            3: (curr[3], fin,),
        }
        angles_speeds = self.kinematics.generateDHAngles(feet, speed)
        self.engine.moveLegsGait4(angles_speeds)
        time.sleep(2)


    # def pose_pt(self, leg, pt, speed):
    #     """
    #     Moves 1 leg to a position
    #     value?
    #     """
    #     pts = {
    #         leg: [pt]
    #     }
    #     angles = self.kinematics.generateServoAngles2(pts, speed)
    #     print(angles)
    #     self.engine.moveLegsGait3(angles)
    #     time.sleep(1)

    # def angleCheckLeg(self, legNum, speed):
    #     """
    #     speed = 1 - 1023 (scalar, all servos move at same rate)
    #     {      step 0          step 1         ...
    #         0: [(t1,t2,t3,t4,speed), (t1,t2,t3,t4,speed), ...] # leg0
    #         2: [(t1,t2,t3,t4,speed), (t1,t2,t3,t4,speed), ...] # leg2
    #         ...
    #     } where t=theta
    #     """
    #     cmds = {}
    #     dh_cmds = [
    #         [0, 0, 0, 0],
    #         [0, 0, 0, 45],
    #         [0, 0, 0, -45],
    #         [0, 0, 0, 0],
    #         [0, 0, 90, 0],
    #         [0, 0, 0, 0],
    #         [0, 90, 0, 0],
    #         [0, 0, 0, 0],
    #         [80, 0, 0, 0],
    #         [-80, 0, 0, 0],
    #         [0, 0, 0, 0],
    #     ]
    #
    #     move = []
    #     for angles in dh_cmds:
    #         s_cmds = []
    #         for a, s in zip(angles, self.kinematics.servos):
    #             s_cmds.append(s.DH2Servo(a))
    #         s_cmds.append(speed)
    #         move.append(s_cmds)
    #     cmds[legNum] = move
    #     print(cmds)
    #     self.engine.moveLegsGait3(cmds)

    # def moveToNeutral(self):
    #     curr = ??
    #     for i in range(4):
    #         if curr[i] != self.positions['stand'][i]:
    #             n = self.positions['stand'][i]
    #             pt = (
    #                 (curr[0], curr[1], 0,),
    #                 (n[0],n[1],0),
    #                 n
    #             )
    #             feet = {}
    #             feet[i] = pt
    #             angles_speeds = self.kinematics.generateServoAngles2(feet, speed)
    #             self.engine.moveLegsGait4(angles_speeds)
    #             time.sleep(1)
    #
    # def moveToStart(self):
    #     curr = ??
    #     start = self.gait.points
    #     for i in range(4):
    #         index = ['A', 'N','N','A']
    #         if curr[i] != start[index[i]]:
    #             n = self.positions['stand'][i]
    #             pt = (
    #                 (curr[0], curr[1], 0,),
    #                 (n[0],n[1],0),
    #                 n
    #             )
    #             feet = {}
    #             feet[i] = pt
    #             angles_speeds = self.kinematics.generateServoAngles2(feet, speed)
    #             self.engine.moveLegsGait4(angles_speeds)
    #             time.sleep(1)

def main():
    test = RobotTest()
    # time.sleep(2)

    try:
        # test.stand()
        # time.sleep(3)
        test.walk()
        # test.angleCheckLeg(0, 200)
        # test.sitstand()
        # test.pose_pt(0, [160, 0, 30], 100)
        # a = [0, 160-123, 130-194, 100-167]
        # print(test.get_point(a))  # (196.89869392004982, 0.0, -76.0225669165195)
        # p = [160,0,-70]
        # print(test.get_angle(p))
        # test.sit()
        # time.sleep(2)
    except KeyboardInterrupt:
        print('bye ...')
        # time.sleep(1)


if __name__ == '__main__':
    main()
