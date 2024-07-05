from cam import CameraBoard
from comms import Comms
import time
from math import floor

cam = CameraBoard(os)
comms = Comms()
comms.create_wifi_connection('wifi_credentials.json')
comms.create_rest_connection("{connection_id}", "{rest_end_point}")

def get_photo():
    buf = cam.take_photo()
    return buf

def convert_score(score):
    return str(floor(score * 100))

# Take a photo and send a post request. The reponses
def analyze_vision():
    try:
        # Returns byte array of photo
        img = get_photo()
        time = cam.get_time()
        photo_label = f"{time}_"
        
        # Query contents of the image. Uses the following model by default
        # https://api-inference.huggingface.co/models/hustvl/yolos-small
        res = comms.img_query("py_anywhere", img)
        print("--------------------------------")
        if len(res) > 0:
            for item in res:
                if len(photo_label) < 30: # Restrict size of filename.
                    photo_label = f"{photo_label}_{item['label']}_{convert_score(item['score'])}"
                print(item)
            cam.save_photo(photo_label, img)
            print(photo_label)
            
        else:
            print("No objects detected")
        analyze_vision()
    except Exception as e:
        print(e)
        time.sleep(3)
        analyze_vision()    

    
def main():
    #comms.post_json("py_anywhere", {'msg': "hello world esp"})
    #comms.post_img("py_anywhere", "final_photo", img)
    #comms.post_query("py_anywhere", "How many suns are in the solar system?")
    cam.cam_init()
    analyze_vision()    
    time.sleep(3)
    comms.wifi.disconnect()
    #cam.close()
    
main()




