# -*- coding: utf-8 -*-
"""
Created on Wed Jul 13 23:11:42 2022

Collect intel data from cmd line 
2 CAMERAS!

Make sure to run the calibration script before begining to collect data

PREPARE THIS SCRIPT AND START WRITING SIMULTANEOUSLY WITH KINECT PARENT CAMERA

@author: lucas
"""

import pyrealsense2 as rs
import numpy as np
#from numpy import array
import cv2
import keyboard
from datetime import date
from datetime import datetime
import time

#copied from this github answer: https://github.com/IntelRealSense/librealsense/issues/1735 and modified

fps = 30 #frames per second
videoDuration = 5 #seconds

#get camera intrinsics and start camera stream
pipeline = rs.pipeline()
cfg = pipeline.start() # Start pipeline and get the configuration it found
profile = cfg.get_stream(rs.stream.depth) # Fetch stream profile for depth stream
intr = profile.as_video_stream_profile().get_intrinsics() # Downcast to video_stream_profile and fetch intrinsics

Cres = [1280, 720]
Dres = [1280, 720]


# Configure depth and color streams...
# ...from Camera 1
pipeline_1 = rs.pipeline()
config_1 = rs.config()
config_1.enable_device('213522250651')
config_1.enable_stream(rs.stream.depth, Dres[0], Dres[1], rs.format.z16, fps)
config_1.enable_stream(rs.stream.color, Cres[0], Cres[1], rs.format.bgr8, fps)
#config_1.enable_stream(rs.stream.infrared, width, height, rs.format.y8, fps)


# ...from Camera 2
pipeline_2 = rs.pipeline()
config_2 = rs.config()
config_2.enable_device('207322251130')
config_2.enable_stream(rs.stream.depth, Dres[0], Dres[1], rs.format.z16, fps)
config_2.enable_stream(rs.stream.color, Cres[0], Dres[1], rs.format.bgr8, fps)
#config_2.enable_stream(rs.stream.infrared, width, height, rs.format.y8, fps)


# Start streaming from both cameras
pipeline_1.start(config_1)
pipeline_2.start(config_2)


##Initialize storage variables
numFrames = fps*videoDuration

depthStore1 = np.empty([numFrames, Dres[1], Dres[0]], dtype=np.float)
depthStore2 = np.empty([numFrames, Dres[1], Dres[0]], dtype=np.float)

colorStore1 = np.empty([numFrames, Cres[1],Cres[0],3], dtype=np.uint8)
colorStore2 = np.empty([numFrames, Cres[1],Cres[0],3], dtype=np.uint8)

print("Cameras are on... press 'w' to start recording data...")


Record = True
j = 0
while Record == True and j == 0:
    if keyboard.is_pressed('w'):
        print("Capturing video...")
        for i in range(numFrames):
            #print(i)
            # Camera 1 and 2
            # Wait for a coherent pair of frames: depth and color
            frames_1 = pipeline_1.wait_for_frames()
            frames_2 = pipeline_2.wait_for_frames()
            
            depth_frame_1 = frames_1.get_depth_frame()
            depth_frame_2 = frames_2.get_depth_frame()
        
            color_frame_1 = frames_1.get_color_frame()
            color_frame_2 = frames_2.get_color_frame()
            
            if not depth_frame_1 or not color_frame_1 or not depth_frame_2 or not color_frame_2: 
                continue
            # Convert depth and color images to numpy arrays
            depth_image_1 = np.asanyarray(depth_frame_1.get_data())
            depth_image_2 = np.asanyarray(depth_frame_2.get_data())
            
            color_image_1 = np.asanyarray(color_frame_1.get_data())
            color_image_2 = np.asanyarray(color_frame_2.get_data())
                    
            #store for post processing after done collecting
            
            colorStore1[i]= color_image_1
            colorStore2[i]= color_image_2
            
            depthStore1[i] = depth_image_1
            depthStore2[i] = depth_image_2
            if i == (numFrames-1):
                print("Capture is over... press 'q' to write to a file")
    if keyboard.is_pressed('q'):
        break

        
            
start = time.time()
# Stop streaming
pipeline_1.stop()
pipeline_2.stop()

print("Writing video now...")

#reshape to be the right size
Depth1 = depthStore1.reshape((depthStore1.shape[0]*depthStore1.shape[1]),depthStore1.shape[2])
Depth2 = depthStore2.reshape((depthStore2.shape[0]*depthStore2.shape[1]),depthStore2.shape[2])

file1 = 'Dev1_RawDepthFrame.txt'
file2 = 'Dev2_RawDepthFrame.txt'
#2 save to txt file
np.savetxt(file1, Depth1, delimiter = ',')
np.savetxt(file2, Depth2, delimiter = ',')



#write video
out1 = cv2.VideoWriter("Device1.MP4", cv2.VideoWriter_fourcc(*'DIVX'), 30, (Cres[0], Cres[1]))
out2 = cv2.VideoWriter("Device2.MP4", cv2.VideoWriter_fourcc(*'DIVX'), 30, (Cres[0], Cres[1]))
for i in range(numFrames):
    out1.write(colorStore1[i])
    out2.write(colorStore2[i])


    

out1.release()
out2.release()
print(time.time()-start)
print("Please move these files to their designated location before running again!")