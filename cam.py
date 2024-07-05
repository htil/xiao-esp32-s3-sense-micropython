import camera
import machine
import utime
from time import sleep

class CameraBoard():
    def __init__(self, os, photo_directory = "/sd/"):
        self.os = os
        self.cam_loading = True
        self.photo_directory = photo_directory

        self.microsd_config = {
            'miso':8,
            'mosi':9,
            'cs':21,
            'sck':7,
        }
        self.sd = machine.SDCard(slot=3, width=1,
                    sck=machine.Pin(self.microsd_config['sck']),
                    mosi=machine.Pin(self.microsd_config['mosi']),
                    miso=machine.Pin(self.microsd_config['miso']),
                    cs=machine.Pin(self.microsd_config['cs']))
        
        self.expansion_board_init()
        
    def cam_init(self):
        while self.cam_loading:
            cam_ready = camera.init() # Camera
            print("Camera ready?: ", cam_ready)
            self.cam_loading = not cam_ready
            sleep(1)
        
    def expansion_board_init(self):
        print("mounting")
        print(self.sd.info())
        self.os.mount(self.sd, "/sd")
        print(self.os.listdir("/sd"))
        
    def get_time(self):
        current_time = utime.localtime()
        hour = current_time[3]
        minute = current_time[4]
        sec = current_time[5]
        return str(hour) + "_" + str(minute) + "_" + str(sec)
    
    def save_photo(self, file_name, data):
        file_path = self.photo_directory + file_name + ".jpg"
        imgFile = open(file_path, "wb")
        imgFile.write(data)
        imgFile.close()
    
    def take_photo(self):
        #self.cam_init()
        p=camera.capture()
        print("photo_captured")
        #self.close()
        return p

    def close(self):
        camera.deinit()

