def execute(self):

    #print ('Execute')
    # TODO

    # Vacuum's yaw
    yaw = self.pose3d.getPose3d().yaw

    # Check crash
    crash = self.checkCrash()

    if crash == 1:
        # Start time
        self.initTime()
        # When there has already been a crash we change the value of self.numCrash to start doing the bump & go
        self.numCrash = 1

    if abs(self.startTime - time.time()) > self.TIME_PERIMETER:
        # Restart variable
        self.foundPerimeter = False

    print("Crash: ", crash)

    if self.numCrash == 0:
        # If self.numCrash equals 0, then we make the spiral
        self.motors.sendW(0.5)
        self.motors.sendV(self.radiusInitial*self.constant)
        self.constant += 0.012
    else:
        if crash == 1 and self.foundPerimeter == False and self.crash == False:
            # Stop
            self.stopVacuum()
            time.sleep(1)
            # Go backwards
            self.motors.sendV(-0.1)
            time.sleep(1)

            self.crash = True
            self.yaw = self.pose3d.getPose3d().yaw
            # Random angle and sign
            self.numAngle = random.uniform(pi/3, pi)
            self.sign = random.randint(0, 1)

        elif abs(self.startTime - time.time()) < self.TIME_PERIMETER:
            # PERIMETER
            self.foundPerimeter = True

            # Get the data of the laser sensor, which consists of 180 pairs of values
            laser_data = self.laser.getLaserData()

            # Distance in millimeters, we change to cm
            laserRight = laser_data.distanceData[0]/10
            laserCenter = laser_data.distanceData[90]/10
            laser45 = laser_data.distanceData[45]/10
            laser135 = laser_data.distanceData[135]/10

            # Calculate the angle of triangle
            a = self.calculateSideTriangle(laserRight, laser45, 45)
            angleC = self.calculateAngleTriangle(a, laserRight, laser45)

            # Turn until the obstacle is to the right
            self.turnUntilObstacleToRight(angleC)

            if self.obstacleRight == True:
                # The obstacle is on the right
                if laserCenter < self.DIST_TO_OBST_FRONT or self.corner == True:
                    # Vacuum is in the corner
                    print ('Vacuum is in the corner ')
                    self.turnCorner(yaw)

                elif crash == 1 and laser135 <= self.DIST_TO_OBST_135:
                    # The vacuum cleaner is stuck
                    self.motors.sendV(-0.3)
                    self.corner = True

                else:
                    # Go next to the wall
                    print("Go next to the wall")
                    self.goNextToWall(laserRight, laser45)
                    self.yaw = yaw
                    self.firstCrash = False


        elif self.turn == False and self.crash == True:
            # Rotate the self.numAngle

            # yawNow is the orientation that I have at the moment
            yawNow = self.self.pose3d.getPose3d().yaw

            # Conversion of angles
            self.yaw = self.convert2PiTo0(self.yaw)
            yawNow = self.convert2PiTo0(yawNow)

            if (-pi < self.yaw < -pi/2) or (-pi < yawNow < -pi/2):
                # Conversion of angles
                self.yaw = self.add2Pi(self.yaw, yawNow)
                yawNow = self.add2Pi(yawNow, self.yaw)

            # Calculate the difference between angles and do the turn
            angle = abs(self.yaw - yawNow)
            self.turn = self.turnAngle(angle)

        else:
            # Go forward
            self.motors.sendW(0)
            time.sleep(1)
            self.motors.sendV(0.5)

            # Restart global variables
            self.crash = False
            self.turn = False
                
vc.setExecute(execute)