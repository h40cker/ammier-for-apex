import argparse
from screenshots import *
import time
from pynput import mouse, keyboard
from MyListener import listen_key, listen_mouse, get_S_L, Mouse_redirection, Move_Mouse
from args_ import *
from threading import Thread
from multiprocessing import Process, Pipe, Value
from show_target import Show_target
import numpy as np

global Start_detection, Listen
# Start listen the right mouse button and the esc
def listeners():
    key_listener = keyboard.Listener(on_press=listen_key)
    key_listener.start()

    mouse_listener = mouse.Listener(on_click=listen_mouse)
    mouse_listener.start()
    print("listener start")
    key_listener.join()

count=0
interval=0.03
if __name__ == "__main__":
    # create a arg set
    Listen=True

    args = argparse.ArgumentParser()
    args = arg_init(args)

    process1 = Thread(
        target=listeners,
        args=(),
    )
    process1.start()

    #Mouse_mover = Thread(target=Move_Mouse, args=(args,), name="Mouse_mover")
    #Mouse_mover.start()
    shot_init(args)
    if args.model[-3:]==".pt":
        from predict import *
        predict_init(args)
    else:
        from trt import predict_trt, predict_init
        predict_init(args)
    print("Main start")
    time_start = time.time()
    while Listen:
        
        Start_detection, Listen = get_S_L()
        # take a screenshot
        #time_shot=time.time()
        img=take_shots(args)
        #print("shots time: ", time.time() - time_shot)
        # predict the image
        #print("shot+predict time: ", time.time() - time_start)
        time.sleep(args.wait)
        if args.model[-3:]==".pt":
            predict_res = predict(args,img)
            boxes = predict_res.boxes
            boxes = boxes[boxes[:].cls == args.target_index].cpu().xyxy.numpy()
        else:
            boxes = predict_trt(args,img)
        if Start_detection :
            #print(boxes)
            Mouse_redirection(boxes, args, interval)
            Move_Mouse(args)
        #print("total time: ", time.time() - time_start)
        count+=1

        if(count%100==0):        
            time_per_100frame = time.time() - time_start
            time_start = time.time()
            print("fps: ", count/time_per_100frame)
            interval=time_per_100frame/count
            print("interval: ",interval)
            count=0
        

    print("main over")
