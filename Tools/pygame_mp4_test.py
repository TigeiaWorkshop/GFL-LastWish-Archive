# -*- coding:utf-8 -*-
import pygame
import sys
import cv2
import numpy as np
import os


# 初始化,并读取第一帧
# rval表示是否成功获取帧
# frame是捕获到的图像
vc = cv2.VideoCapture("../Assets/movie/SquadAR.mp4")

# 获取视频fps
fps = vc.get(cv2.CAP_PROP_FPS)
# 获取视频总帧数
frame_all = vc.get(cv2.CAP_PROP_FRAME_COUNT)

print("[INFO] 视频总帧数: {}".format(frame_all))

the_list = []

for i in range(int(frame_all)):
    ret, frame = vc.read()
    try:
        frame = np.rot90(frame,k=-1)
    except:
        continue
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = np.rot90(frame,k=-1)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) 
    frame = pygame.surfarray.make_surface(frame)
    frame=pygame.transform.flip(frame,False,True)
    the_list.append(frame)
    print(i)

print(len(the_list))
