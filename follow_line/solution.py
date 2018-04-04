def execute(self):
        #GETTING THE IMAGES
        input_image = self.getImage()

        # Add your code here
        print "Runing"

        #EXAMPLE OF HOW TO SEND INFORMATION TO THE ROBOT ACTUATORS
        #self.motors.sendV(10)
        #self.motors.sendW(5)

        # saving segmented image
        #self.set_threshold_image(input_image_copy)

        # RGB model change to HSV
        image_HSV = cv2.cvtColor(input_image, cv2.COLOR_RGB2HSV)

        # Minimum and maximum values of the red ​​
        value_min_HSV = np.array([0, 235, 60])
        value_max_HSV = np.array([180, 255, 255])

        # Filtering images
        image_HSV_filtered = cv2.inRange(image_HSV, value_min_HSV, value_max_HSV)


        # Creating a mask with only the pixels within the range of red
        image_HSV_filtered_Mask = np.dstack((image_HSV_filtered, image_HSV_filtered, image_HSV_filtered))


        # Shape gives us the number of rows and columns of an image
        size = input_image.shape
        rows = size[0]
        columns = size[1]


        #  Looking for pixels that change of tone
        position_pixel_left = []
        position_pixel_right  = []

        for i in range(0, columns-1):
            value = image_HSV_filtered
            if(value.all != 0):
                if (value.all == 255):
                    position_pixel_left.append(i)
                else:
                    position_pixel_right.append(i-1)


        # Calculating the intermediate position of the road
        if ((len(position_pixel_left) != 0) and (len(position_pixel_right) != 0)):
            position_middle = (position_pixel_left[0] + position_pixel_right[0]) / 2
        elif ((len(position_pixel_left) != 0) and (len(position_pixel_right) == 0)):
            position_middle = (position_pixel_left[0] + columns) / 2
        elif ((len(position_pixel_left) == 0) and (len(position_pixel_right) != 0)):
            position_middle = (0 + position_pixel_right[0]) / 2
        else:
            position_pixel_right.append(1000)
            position_pixel_left.append(1000)
            position_middle = (position_pixel_left[0] + position_pixel_right[0])/ 2


        # Calculating the desviation
        desviation = position_middle - (columns/2)
        print (" desviation    ", desviation)

        #EXAMPLE OF HOW TO SEND INFORMATION TO THE ROBOT ACTUATORS
        if (desviation == 0):
             self.motors.sendV(5)
        elif (position_pixel_right[0] == 1000):
             self.motors.sendW(-0.0000035)
        elif ((abs(desviation)) < 85):
             if ((abs(desviation)) < 15):
                 self.motors.sendV(1.5)
             else:
                 self.motors.sendV(3.5)
             self.motors.sendW(-0.000045 * desviation)
        elif ((abs(desviation)) < 150):
             if ((abs(desviation)) < 120):
                 self.motors.sendV(1)
             else:
                 self.motors.sendV(1.5)
             self.motors.sendW(-0.00045 * desviation)
        else:
             self.motors.sendV(1.5)
             self.motors.sendW(-0.0055 * desviation)


        # Saving the filtered image
        self.set_threshold_image(image_HSV_filtered_Mask)
        
fl.setExecute(execute)