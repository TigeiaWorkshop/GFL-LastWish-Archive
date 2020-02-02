# -*- coding:utf-8 -*-
import pygame
import sys
import cv2
import numpy as np
import os



pygame.init()  # 初始化pygame
#设置窗口位置
size = width, height = 1280, 720  # 设置窗口大小
screen = pygame.display.set_mode(size)  # 显示窗口
videoCapture = cv2.VideoCapture("../Assets/movie/SquadAR.mp4")

while True:
    if videoCapture.isOpened():
        ret, frame = videoCapture.read()
        try:
            frame = np.rot90(frame,k=-1)
        except:
            continue
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) 
        frame = pygame.surfarray.make_surface(frame)
        frame=pygame.transform.flip(frame,False,True)
        screen.blit(frame, (0,0))

    for event in pygame.event.get():  # 遍历所有事件
        if event.type == pygame.QUIT:  # 如果单击关闭窗口，则退出
            sys.exit()



    pygame.display.update()  # 更新全部显示



pygame.quit()  # 退出pygame
