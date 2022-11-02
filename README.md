# IntelRealSense_DataCollectionScripts (In Progress)
Sync Intel RealSense D455 Depth camera streams without the use of an externally generated sync signal AND Automatic camera callibration

I have begun development to record human movement with two Intel RealSense depth cameras. Intel gives instructions in their [white paper](https://support.intelrealsense.com/hc/en-us/community/posts/360046810534-Intel-white-paper-on-external-synchronization-of-RealSense-depth-cameras#:~:text=Intel%20have%20published%20a%20new%20white-paper%20document%20and,using%20the%20new%20Genlock%20function.%20White%20paper%20https%3A%2F%2Fdev.intelrealsense.com%2Fdocs%2Fexternal-synchronization-of-intel-realsense-depth-cameras)
on how to start their cameras in sync with an external signal generator. These scripts attempt to do the same thing using the pyrealsense library, and starting and ending the camera streams at the same time. I recommend recording for no more than 5 seconds at a time, otherwise it may take too long to save the depth information. 
This is still a work in progress, since the data I gathered containes too much noise. An external sync staggers the light each camera projects, reducing optical interference. Forgoing this sync could explain why the data is so dissapointing. However, other programmers using the D455 camera have run into similar issues and are offered no meaningful solutions. The D455 camera has been discontinued, perhaps partly because it doesn't perform as intended. Additionally, Intel is trying to "wind down" their RealSense business, so support for these products will continue to dwindle. 

# Collected Depth Data
Examples of human movement trials I collected using the Intel Camera. Here is the view from one camera straight on, and rotated 45 degrees. As you can see, it's very noisy! And practically unusable. You win some, you lose some. 

Example subject data of a lunge

<img src="https://media.giphy.com/media/CrV2xZA1EIrxVHShlt/giphy.gif" width="1000" />

Example subject data of a sitting to stand activity from a low chair

<img src="https://media.giphy.com/media/yQ5QKwmqPrwjI2WDXH/giphy.gif" width="1000" />

Example subject data of a sitting to stand activity from a high chair

<img src="https://media.giphy.com/media/P0wzgwV7f8YxISkB48/giphy.gif" width="1000" />






# Automatic Calibration 
![1CalCorner_COLOR](https://user-images.githubusercontent.com/67296859/198896030-856d71b2-3d64-4842-aee8-8a3543ae7285.png)
![2CalCorner_COLOR](https://user-images.githubusercontent.com/67296859/198896054-49f9acc9-e7ce-435a-b894-72271e42c13b.png)

Person for scale. These images are generated from the "CMD_Calibrate2IntelCameras.py" script. It is intended to be called from a command line, and guides the user through the code functionality. It uses OpenCV's chessboard detection code to detect chessboard corners in both camera frames. When a chessboard can be seen by both cameras, the stream is shut off and a few files are saved for calibrating (2 copies, one from each camera):
1. The RGB image of the chessboard
2. The pixel coordinates of the chessboard corners
3. The depth image of the chessboard. 

# Plan for Automatic Calibration
Work for this has paused temporarily after realizing the depth data from the RealSense cameras is unusable. The end goal for this saved information is to reconstruct the 3D coordinate of each detected corner. The chessboard (one object in the world coordinate system) is viewed by two cameras that capture the color pixel coordinates in their own camera coordinate system. 
![image](https://user-images.githubusercontent.com/67296859/198897985-fb1805a4-d553-473b-837c-b8ae88f07b96.png)
The depth coordinate of each corner can be found using intrinsic and extrinstic parameters of the RGB and depth cameras. After mean centering the acquired sets of corners, the optimal rotation matrix can be found to align them into one coordinate system. The rotation matrix can "stitch together" the data gathered from two cameras. 
