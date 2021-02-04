import av
import pygame
import numpy as np

pygame.init()
soundPath = "..\Assets\music/First_Kiss.mp3"
sound_in_pg = pygame.mixer.Sound(soundPath)

soundArray = np.array(sound_in_pg,dtype=np.float32, copy=True)


video_container = av.open(soundPath,mode='r')
audio_stream = video_container.streams.audio[0]
audio_stream.thread_type = 'AUTO'

resample_audio = av.audio.resampler.AudioResampler(format='s16p')



"""
sound_list = []
for frame in video_container.decode(audio_stream):
    frame.pts = None
    frame = resample_audio.resample(frame)
    frame_np_array = frame.to_ndarray()
    for i in range(len(frame_np_array[0])):
        sound_list.append([frame_np_array[0][i],frame_np_array[1][i]])
    
"""

#sound_list = np.asarray(sound_list)

sound_in_pg = pygame.mixer.Sound(array = {})
while True:
    sound_in_pg.play()
