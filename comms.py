from micropython import const
import uasyncio as asyncio
import aioble
import bluetooth
import struct
from machine import Pin
from random import randint
import network
import urequests as requests
import ujson
import utime

class Wifi():
    def __init__(self, credentials_file):
        print("init wifi")
        self.credentials_file = credentials_file
        credentials = self.load_wifi_credentials()
        self.ssid = credentials['ssid']
        self.password = credentials['password']
        self.sta = None
        self.connect_s3()
    
    def load_wifi_credentials(self):
        try:
            with open(self.credentials_file, 'r') as file:
                data = ujson.load(file)
            return data
        except:
            raise RuntimeError(f"unable to find {self.credentials_file} file")
        
        
    def connect_s3(self):
        self.sta = network.WLAN(network.STA_IF)
        try:
            self.sta.disconnect()
        except Exception as e:
            print(e)
        
        self.sta.active(True)
        # Fill in your network name (SSID) and password here:
        if not self.sta.isconnected():
            self.sta.connect(self.ssid, self.password)
            print("connecting....")
            while not self.sta.isconnected():
                utime.sleep(1)  # sleep for a second
            print("Network connected")

    def connect(self):
        self.sta = network.WLAN(network.STA_IF)
        #self.sta.disconnect()
        if not self.sta.isconnected():
            print('connecting to network...')
            self.sta.active(True)
            self.sta.connect(self.ssid, self.password)
            while not self.sta.isconnected():
                pass
            print("wifi connected")
            #self.post_req()
            return 0
        print("wifi connected")
        #self.post_req()
    
    def disconnect(self):
        self.sta.disconnect()
        print(self.ssid + " disconnected")
        

class BLE():
    def __init__(self, service_uuid, name):
        self.service_uuid = bluetooth.UUID(service_uuid)
        self.service = self._register_service(self.service_uuid)
        self.name = name
        self.characteristics = {}
        self.ADV_INTERVAL_MS = 250_000
        print("init BLE.")
    
        
    # Helper to encode the data characteristic UTF-8
    def _encode_data(self, data):
        return str(data).encode('utf-8')
    
    # Helper to decode string data
    def _decode_str(self, data):
        try:
            string_msg = data.decode("utf-8")
            return string_msg
        except Exception as e:
            print("Error decoding data:", e)
            return None
    
    # Helper to decode int data
    def _decode_int(self, data):
        try:
             number = int.from_bytes(data, 'big')
             return number
        except Exception as e:
            print("Error decoding data:", e)
            return None
    
    def _add_characteristic(self, id, characteristic):
        self.characteristics[id] = characteristic
        
    def get_characteristics(self):
        print(self.characteristics)
        return self.characteristics
        
    def register_characteristic(self, characteristic_id, UUID, read=False, write=False, notify=False, capture=False):
        if self.service is not None:
            UUID = bluetooth.UUID(UUID)
            _characteristic =  aioble.Characteristic(self.service, UUID, read=read, notify=notify, write=write, capture=capture)
            self._add_characteristic(characteristic_id, _characteristic)
        else:
            print("Service not defined.")
    
    def remove_characteristic(self, id, characteristic):
        self.characteristics[id].pop()
        
    def _register_service(self, UUID):
        print(aioble)
        return aioble.Service(self.service_uuid)
    

    def register_services(self):
        aioble.register_services(self.service)
    
    # Get sensor readings
    def get_random_value(self):
        return randint(0,100)
    
    def write_characteristic(self, value, characteristic):
        self.characteristics[characteristic].write(self._encode_data(value), send_update=True)

    # Get new value and update characteristic
    async def sensor_task(self, characteristic, sensor_callback):
        while True:
            value = sensor_callback()
            #self.write_characteristic(value, characteristic)
            self.characteristics[characteristic].write(self._encode_data(value), send_update=True)
            #print('New random value written: ', value)
            await asyncio.sleep_ms(1000)
            
    async def wait_for_int_write(self, characteristic):
        while True:
            try:
                connection, data = await self.characteristics[characteristic].written()
                number = self._decode_int(data)
                print("number: " + number)
            except Exception as e:
                print("Error decoding int data:", e)
                return None
            
    async def wait_for_str_write(self, characteristic):
        while True:
            try:
                connection, data = await self.characteristics[characteristic].written()
                string = self._decode_str(data)
                print("string: " + string)
            except Exception as e:
                print("Error decoding int data:", e)
                return None
                 
    # Serially wait for connections. Don't advertise while a central is connected.
    async def wait_for_connection(self):
        print("INTERVAL: " + " " + str(self.ADV_INTERVAL_MS))
        print("Service UUID: " + " " + str(self.service_uuid))
        while True:
            try:
                async with await aioble.advertise(
                    self.ADV_INTERVAL_MS,
                    name=self.name,
                    services=[self.service_uuid],
                    ) as connection:
                        print("Connection from", connection.device)
                        await connection.disconnected()             
            except asyncio.CancelledError:
                # Catch the CancelledError
                print("Peripheral task cancelled")
            except Exception as e:
                print("Error in peripheral_task:", e)
            finally:
                # Ensure the loop continues to the next iteration
                await asyncio.sleep_ms(100)

class MQTT_CLIENT_COMM():
    def __init__(self):
        print("init mqtt client")
    
    def create_mqtt_connection(self):
        print("create_mqtt_connection")
    
class Comms():
    def __init__(self):
        self.ble = None
        self.wifi = None
        self.mqtt = None
        self.rest_connections = {}
        print("init comms")
    
    def create_ble_connection(self, service_uuid, name):
        self.ble = BLE(service_uuid, name)
        return self.ble

    def create_wifi_connection(self, credentials_file):
        self.wifi = Wifi(credentials_file)
        
    def create_rest_connection(self, end_point_id, base_url):
        self.rest_connections[end_point_id] = REST(base_url)
        print(self.rest_connections)
    
    def get_rest_connection(self, end_point_id):
        return self.rest_connections[end_point_id]
    
    def post_json(self, end_point_id, json):
         self.rest_connections[end_point_id].post_json(json)
    
    def post_query(self, end_point_id, query):
         self.rest_connections[end_point_id].post_query(query)
    
    def post_img(self, end_point_id, file_name, img):
         self.get_rest_connection(end_point_id).post_img(file_name, img)
    
    def img_query(self, end_point_id, img, query_type="yolo"):
         return self.get_rest_connection(end_point_id).img_query(img, query_type)
        
    def is_wifi_connected(self):
        return network.WLAN(network.STA_IF).isconnected()
            
class REST():
    def __init__(self, end_point_url):
        self.end_point = end_point_url
        
    def post_json(self, json_obj):
        #BASE_URL = f"https://northcsc.pythonanywhere.com/?input=esp"
        print(f"POST: {self.end_point}")
        post_data = ujson.dumps(json_obj)
        res = requests.post(url=self.end_point, headers = ({'content-type': 'application/json'}), data = (post_data)).json()
        #print(res)
        return res
    
    def post_query(self, query, query_type="sentiment"):
        _headers =  {'content-type': 'application/json'}
        _end_point = f"{self.end_point}/{query_type}/"
        json_obj = ujson.dumps({'input': query})
        res = requests.post(url=_end_point, headers = (_headers), data = (json_obj)).json()
        print(res)
        
    def post_img(self, file_name, img):
        _headers =  {'content-type': 'image/jpeg'}
        _end_point = f"{self.end_point}/?file_name={file_name}"
        print("end_point")
        print(_end_point)
        res = requests.post(url=_end_point, headers = (_headers), data = (img)).json()
        print(res)
        return res
    
    def img_query(self, img, query_type="yolo"):
        _headers =  {'content-type': 'image/jpeg'}
        _end_point = f"{self.end_point}/{query_type}/"
        print("request_sent")
        res = requests.post(url=_end_point, headers = (_headers), data = (img)).json()
        return res
    
