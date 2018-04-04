def execute(self):

    # TODO
    '''
    # Time to check saturation
    self.initSatTime()

    # Check saturation
    self.checkSaturationVacuum()

    # Change and show grid
    self.changeValuesGrid()
    self.showGrid()
    '''
    # Vacuum's poses
    x = self.pose3d.getPose3d().x
    y = self.pose3d.getPose3d().y
    yaw = self.pose3d.getPose3d().yaw

    # Check crash
    crash = self.checkCrash()

    self.changeMap()

    if self.saturation == False:
        if crash == 1 and self.crash == False:
            print ("CRAAASH")
            # Stop and go backwards
            self.stopAndBackwards()

            # Yaw
            yaw = self.pose3d.getPose3d().yaw
            self.firstTurn = False
            self.crash = True

        if self.firstTurn == False and self.crash == True:
            print ("First turn")
            # Yaw
            yawNow = self.pose3d.getPose3d().yaw
            # Orientation
            self.orientation = self.returnOrientation(self.yaw)
            # Turn 90
            giro = self.turn90(pi/2, pi/2, yawNow)

            if giro == False:
                print ("Turn done")
                self.firstTurn = True
                # Go forwards
                self.goForward(0.2)
                time.sleep(1)
                self.secondTurn = False

        elif self.secondTurn == False and self.crash == True:
            print ("Second turn")
            # Yaw
            yawNow = self.pose3d.getPose3d().yaw
            giro = self.turn90(pi, 0, yawNow)

            if giro == False:
                self.secondTurn = True

        else:
            print ("Go forward...")
            # Go forward
            self.goForward(0.5)
            self.crash = False
            self.firstTurn = True

    else:
        # There is saturation
        print ("PERIMETER")

        # Get the data of the laser sensor, which consists of 180 pairs of values
        laser_data = self.laser.getLaserData()

        # Distance in millimeters, we change to cm
        laserRight = laser_data.distanceData[0]/10
        laserCenter = laser_data.distanceData[90]/10
        laser45 = laser_data.distanceData[45]/10

        # Calculate the angle of triangle
        a = self.calculateSideTriangle(laserRight, laser45, 45)
        angleC = self.calculateAngleTriangle(a, laserRight, laser45)

        # Initialize start time
        self.initPerimTime()
        timeNow = time.time()

        # Only walks the wall for a while
        if self.startTime - timeNow < self.TIME_PERIM:
            if crash == 0 and self.crashObstacle == False:
                # I go forward until I find an obstacle
                self.goForward(0.5)
                print("GO FORWARD")
            elif crash == 1 and self.crashObstacle == False:
                self.crashObstacle = True
                print("NEW CRASH")
                # Stop and go backwards
                self.stopAndBackwards()

            if self.crashObstacle == True:
                # Turn until the obstacle is to the right
                self.turnUntilObstacleToRight(angleC)

                if self.obstacleRight == True:
                    # The obstacle is on the right
                    if laserCenter < self.DIST_TO_OBST_FRONT or self.corner == True:
                        # Vacuum is in the corner
                        print ('Vacuum is in the corner ')
                        self.turnCorner(yaw)

                    else:
                        # Go near to the wall
                        print("Go near to the wall")
                        self.goNearToWall(laserRight)
                        self.yaw = yaw

        else:
            # Restart all global variables
            self.restartVariables()