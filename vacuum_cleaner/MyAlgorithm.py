#!/usr/bin/python
#-*- coding: utf-8 -*-

import numpy as np
import threading
import time
from datetime import datetime
import jderobot
import math

from math import pi as pi
import random

time_cycle = 80


class MyAlgorithm(threading.Thread):

    def __init__(self, motors, pose3d, laser, bumper):
        self.pose3d = pose3d
        self.motors = motors
        self.laser = laser
        self.bumper = bumper

        self.radiusInitial = 0.1
        self.constant = 0.01
        self.numCrash = 0
        self.yaw = 0
        self.numAngle = 0
        self.sign = 0

        self.turn = False
        self.crash = False
        self.firstCrash = True
        self.obstacleRight = False
        self.corner = False
        self.foundPerimeter = False

        self.startTime = 0

        self.TIME_PERIMETER = 400
        self.MARGIN = 0.2
        self.MARGIN_OBST_RIGHT = 0.1
        self.DIST_TO_OBST_RIGHT = 30
        self.DIST_MIN_TO_OBST_RIGHT = 15
        self.DIST_TO_OBST_FRONT = 15
        self.DIST_TO_OBST_45 = 22
        self.DIST_TO_OBST_135 = 18

        self.stop_event = threading.Event()
        self.kill_event = threading.Event()
        self.lock = threading.Lock()
        threading.Thread.__init__(self, args=self.stop_event)


    def parse_laser_data(self,laser_data):
        laser = []
        for i in range(laser_data.numLaser):
            dist = laser_data.distanceData[i]/1000.0
            angle = math.radians(i)
            laser += [(dist, angle)]
        return laser

    def laser_vector(self,laser_array):
        laser_vectorized = []
        for d,a in laser_array:
            x = d * math.cos(a) * -1
            y = d * math.sin(a) * -1
            v = (x, y)
            laser_vectorized += [v]
        return laser_vectorized

    def run (self):
        while (not self.kill_event.is_set()):

            start_time = datetime.now()

            if not self.stop_event.is_set():
                self.algorithm()

            finish_Time = datetime.now()

            dt = finish_Time - start_time
            ms = (dt.days * 24 * 60 * 60 + dt.seconds) * 1000 + dt.microseconds / 1000.0
            #print (ms)
            if (ms < time_cycle):
                time.sleep((time_cycle - ms) / 1000.0)

    def stop (self):
        self.motors.sendV(0)
        self.motors.sendW(0)
        self.stop_event.set()

    def play (self):
        if self.is_alive():
            self.stop_event.clear()
        else:
            self.start()

    def kill (self):
        self.kill_event.set()


    def initTime(self):
        if self.startTime == 0:
            self.startTime = time.time()


    def checkCrash(self):
        for i in range(0, 350):
            # Returns 1 if it collides, and 0 if it doesn't collide
            crash = self.bumper.getBumperData().state
            if crash == 1:
                self.motors.sendW(0)
                self.motors.sendV(0)
                break
        return crash

    def stopVacuum(self):
        self.motors.sendW(0)
        self.motors.sendV(0)

    def convert2PiTo0(self, angle):
        if angle == 2*pi:
            angle = 0
        return angle

    def add2Pi(self, angle1, angle2):
        if (-pi < angle1 < -pi/2) and ((pi/2 <= angle2 <= pi) or (0 <= angle2 <= pi/2)):
            angle1 = angle1 + 2*pi
        return angle1

    def turnAngle(self, angle):
        turn = False
        if angle <= (self.numAngle-self.MARGIN) or angle >= (self.numAngle+self.MARGIN):
            self.motors.sendV(0)
            if self.sign == 1:
                self.motors.sendW(0.2)
            else:
                self.motors.sendW(-0.2)
        else:
            turn = True
        return turn

    def calculateSideTriangle(self, a, b, angle):
        c = math.sqrt(pow(a,2) + pow(b,2) - 2*a*b*math.cos(angle))
        return c

    def calculateAngleTriangle(self, a, b, c):
        numer = pow(a,2) + pow(b,2) - pow(c,2)
        deno = 2 * a * b
        angleC = math.acos(numer/deno)
        return angleC


    def turnUntilObstacleToRight(self, angle):
        # Turn until the obstacle is to the right
        if (angle >= pi/2 + self.MARGIN_OBST_RIGHT or angle <= pi/2 - self.MARGIN_OBST_RIGHT) and self.obstacleRight == False:
            # Turn to left
            self.motors.sendV(0)
            self.motors.sendW(0.2)
        else:
            self.obstacleRight = True
            self.motors.sendW(0)


    def turnCorner(self, yaw):
        self.corner = True
        # Stop
        self.motors.sendV(0)

        # Conversion of angles
        if self.yaw <= (pi + self.MARGIN) and self.yaw >= (pi - self.MARGIN):
            self.yaw = -pi

        # Gira 90 grados a la izq
        self.orientation = 'left'
        self.numAngle = self.yaw + pi/2
        self.sign = 1
        giro = self.turnAngle(yaw)

        if giro == True:
            self.motors.sendW(0)
            self.corner = False


    def goNextToWall(self, laserRight, laser45):
        if laserRight <= self.DIST_MIN_TO_OBST_RIGHT:
            # Turn to left
            self.motors.sendV(0)
            self.motors.sendW(0.1)
        elif laserRight >= self.DIST_TO_OBST_RIGHT and laser45 >= self.DIST_TO_OBST_45 or self.firstCrash == True:
            # Turn to right
            self.motors.sendV(0)
            self.motors.sendW(-0.1)
        else:
            self.motors.sendW(0)
            self.motors.sendV(0.1)

    def algorithm(self):
        # Add your code here
        pass