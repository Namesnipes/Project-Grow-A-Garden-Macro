import pydirectinput
import pytweening
import time
time.sleep(2)
pydirectinput.PAUSE = 0.01 # Temporarely, because this part would be too slow otherwise
for i in range(1, 100):
    pydirectinput.moveRel(0,int(200*pytweening.easeOutCirc(i/100))) # A fucking genius way of bypassing what I think is Roblox trying to prevent robotic mouse movement
    print(int(200*pytweening.easeOutCirc(i/100)))
pydirectinput.PAUSE = 0.05