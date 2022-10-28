%% Depth Video Creation - Example Script
clear
clc
close all

v = VideoWriter('VIDEO_NAME','MPEG-4');
v.Quality = 100;
v.FrameRate = 10;

theta = pi;

%Useful rotation matrices
%Data is sometimes in a strange coordinate system
rotZ = rotz(180); %Rotate in Z axis
rotY = roty(-45);
rotY1 = roty(45);
trans = [0 0 0];
tform1 = rigid3d(rotZ,trans);
tform2 = rigid3d(rotY,trans);
tform3 = rigid3d(rotY1,trans);
len = 150; %num of groups


for i=1:len
    s = num2str(i);
    path = strcat('frame',s,'.pcd')
    ptCloud = pcread(path);
    ptCloudOut = pctransform(ptCloud, tform1);
    ptCloudOut2 = pctransform(ptCloudOut, tform2); %view point cloud from at a 45 degree angle
    
    figure(1)
    figure('Units','normalized','Position',[0 0 1 1])
    hold all
    subplot(1,2,1);
    pcshow(ptCloudOut)
    view(2)
    xlim([-1.5, 1.5]);
    ylim([-2, 0.5]);
% %     zlim([-1400, 3500]);
    axis off
% % 
    subplot(1,2,2);
    pcshow(ptCloudOut2)
    view(2)
    xlim([1.5, 3.75]);
    ylim([-2, 0.5]);
%     zlim([-1400, 3500]);
    axis off

    
%     subplot(1,3,1);
%     pcshow(ptCloudOut4)
%     view(2)
%     xlim([-3000, 0]);
%     ylim([-3000, 3000]);
%     zlim([-3500, 3500]);
%     axis off

    F(i) = getframe(gcf);  
end
open(v);
for i=1:len
    frame = F(i);
    writeVideo(v,frame);
end
close(v);

