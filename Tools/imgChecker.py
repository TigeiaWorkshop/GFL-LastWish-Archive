import cv2
import numpy as np
import yaml
#933
#1895
for i in range(3106,375,-1):
    img1 = cv2.imread("../Assets/img/SquadAR/bgImg"+str(i)+".jpg")

    for a in range(i-1,375,-1):
        print("Now is checking "+str(i)+" and "+str(a))
        img2 = cv2.imread("../Assets/img/SquadAR/bgImg"+str(a)+".jpg")
        difference = cv2.subtract(img1, img2)
        result = not np.any(difference)
        if result is True:
            print(str(i)+" and " +str(a)+" is the same")
            with open("outputR.yaml", "r", encoding='utf-8') as f:
                setting = yaml.load(f.read(),Loader=yaml.FullLoader)
                the_list = setting['resultWas']
            the_line = str(i)+" and " +str(a)+" is the same"
            the_list.append(the_line)
            with open("outputR.yaml", "w", encoding='utf-8') as f:
                setting['resultWas'] = the_list
                yaml.dump(setting, f)
