# -*- coding: utf-8 -*-
"""
Created on Mon Jul 11 14:34:38 2022

@author: Emma Young

Run intel realsense cameras and gather calibration data

NECESSARY: a chessboard for calibration with known parameters (inside corner dimesions and square size)
"""
import pyrealsense2 as rs
import numpy as np
import cv2
import keyboard
from datetime import date
from datetime import datetime

#Found a lot of assistance from this github answer: https://github.com/IntelRealSense/librealsense/issues/1735 and modified
#Possible useful information for turning detected corners into 3d coordinates:
#https://learnopencv.com/camera-calibration-using-opencv/


fps = 30 #frames per second
videoDuration = 5 #seconds

#get camera intrinsics and start camera stream
pipeline = rs.pipeline()
cfg = pipeline.start() # Start pipeline and get the configuration it found
profile = cfg.get_stream(rs.stream.depth) # Fetch stream profile for depth stream
intr = profile.as_video_stream_profile().get_intrinsics() # Downcast to video_stream_profile and fetch intrinsics


height = intr.height
width = intr.width
size = (width, height)

Cres = [1280, 720]
Dres = [1280, 720]

# Configure depth and color streams...
# ...from Camera 1
pipeline_1 = rs.pipeline()
config_1 = rs.config()
config_1.enable_device('213522250651') #unique camera serial number
config_1.enable_stream(rs.stream.depth, Dres[0], Dres[1], rs.format.z16, fps)
config_1.enable_stream(rs.stream.color, Cres[0], Cres[1], rs.format.bgr8, fps)
#config_1.enable_stream(rs.stream.infrared, width, height, rs.format.y8, fps)


# ...from Camera 2
pipeline_2 = rs.pipeline()
config_2 = rs.config()
config_2.enable_device('207322251130') #unique camera serial number
config_2.enable_stream(rs.stream.depth, Dres[0], Dres[1], rs.format.z16, fps)
config_2.enable_stream(rs.stream.color, Cres[0], Cres[1], rs.format.bgr8, fps)
#config_2.enable_stream(rs.stream.infrared, width, height, rs.format.y8, fps)


# Start streaming from both cameras
pipeline_1.start(config_1)
pipeline_2.start(config_2)


chessboard_params = [1, 2, 3]
chessboard_params[0] =  7 #number of inside corners in y
chessboard_params[1] =  11 #number of inside corners in x
chessboard_params[2] = 0.95#squaresize
numCorn = chessboard_params[0]*chessboard_params[1]
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER,30,0.001)

#create vector to store vectors of 3D points for each checkerboard image
objpoints1 = []
objpoints2 = []
#create a vector to store vectors of 2D points for each checkerboard image
imgpoints1 = []
imgpoints2 = []
#define the world coordinates for 3D points
objp1 = np.zeros((1, chessboard_params[0] * chessboard_params[1], 3), np.float32)
objp1[0,:,:2] = np.mgrid[0:chessboard_params[0], 0:chessboard_params[1]].T.reshape(-1, 2)

objp2 = np.zeros((1, chessboard_params[0] * chessboard_params[1], 3), np.float32)
objp2[0,:,:2] = np.mgrid[0:chessboard_params[0], 0:chessboard_params[1]].T.reshape(-1, 2)
prev_img_shape = None




#Collect time and date for naming file
now = datetime.now()
current_time = now.strftime("_%H_%M_%S")
today = date.today()
current_day = today.strftime("_%m_%d_%y")
timestamp = str(current_day) + str(current_time)


print("Testing video stream. Stream will close when the calibration chessboard can be see with both cameras")
while True:
    frames_1 = pipeline_1.wait_for_frames()
    frames_2 = pipeline_2.wait_for_frames()

    color_frame_1 = frames_1.get_color_frame()
    color_image_1 = np.asanyarray(color_frame_1.get_data())

    depth_frame_1 = frames_1.get_depth_frame()

    color_frame_2 = frames_2.get_color_frame()
    color_image_2 = np.asanyarray(color_frame_2.get_data())

    depth_frame_2 = frames_2.get_depth_frame()

    cv2.imshow("device1", color_image_1)
    cv2.imshow("device2", color_image_2)
    cv2.waitKey(1)

    retval1, corners1 = cv2.findChessboardCorners(color_image_1, (chessboard_params[0], chessboard_params[1]))
    retval2, corners2 = cv2.findChessboardCorners(color_image_2, (chessboard_params[0], chessboard_params[1]))

    if retval1 == True and retval2 == True:
        gray1 = cv2.cvtColor(color_image_1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(color_image_2, cv2.COLOR_BGR2GRAY)
        print("Chessboard is found in both cameras!")
        objpoints1.append(objp1)
        objpoints2.append(objp2)
        
        #refine pixel coordinates
        corners11 = cv2.cornerSubPix(gray1, corners1, (11,11),(-1,-1),criteria)
        corners22 = cv2.cornerSubPix(gray2, corners2, (11,11),(-1,-1),criteria)
        
        imgpoints1.append(corners11)
        imgpoints2.append(corners22)
        
        depth_image_1 = np.asanyarray(depth_frame_1.get_data())
        depth_image_2 = np.asanyarray(depth_frame_2.get_data())
        
        file1 = "1CalCorner_2dCOORDS" + timestamp + '.txt'

        file2 = "2CalCorner_2dCOORDS" + timestamp + '.txt'

        np.savetxt(file1, corners11.reshape(numCorn,2), delimiter = ',')

        np.savetxt(file2, corners22.reshape(numCorn,2), delimiter = ',')
        
        file3 = "1CalCorner_RAWDEPTH" + timestamp + '.txt'

        file4 = "2CalCorner_RAWDEPTH" + timestamp + '.txt'
        
        np.savetxt(file3, depth_image_1, delimiter = ',')

        np.savetxt(file4, depth_image_2, delimiter = ',')
        

        cv2.waitKey(0)
        cv2.destroyAllWindows()
        break
    
    if retval1 == True:
        print("camera1 sees the target")
    elif retval2 == True:
        print("camera2 sees the target")

    if keyboard.is_pressed('q'):
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        break
        
pipeline_1.stop()
pipeline_2.stop()


#Vertify the corners have been placed correctly
drawn11 = cv2.drawChessboardCorners(color_image_1, (7,11), corners11, retval1)
drawn22 = cv2.drawChessboardCorners(color_image_2, (7,11), corners22, retval2)

#write new pictures to file
cv2.imwrite('1CalCorner_VALIDATION.png',drawn11)
cv2.imwrite('2CalCorner_VALIDATION.png',drawn22)

#write undrawn pictures to file
cv2.imwrite('1CalCorner_COLOR.png',color_image_1)
cv2.imwrite('2CalCorner_COLOR.png',color_image_2)


