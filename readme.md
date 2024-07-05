# Summary

Example project demonstrating how to use Xiao Sense ESP32 sense device to capture connect to wifi, BLE, capture photos, and send REST requests.


# Sample Programs

### Save photo
```python
from cam import CameraBoard

cam = CameraBoard(os)
image_data = cam.take_photo()
cam.save_photo("my_image_2", image_data)
```


### Connect wifi
```python
from comms import Comms

comms = Comms()
comms.create_wifi_connection('wifi_credentials.json')
```

### Example BLE App
Note: Requires modification of `wait_for_connection`, `wait_for_str_write`, and `sensor_task` if seeking custom solution.

See [BLE Web App](https://github.com/htil/ble-esp32-webapp) for web app source code.
```python
from comms import Comms
import uasyncio as asyncio
from random import randint

# Get sensor readings
def get_random_value():
    return randint(0,10)

# Create Comms Object
comms = Comms()

# Create BLE Object and register ble service
comms.create_ble_connection('19b10000-e8f2-537e-4f6c-d104768a1214', "ESP32")
#comms.create_wifi_connection('wifi_credentials.json')

# Create Sensor characteristic
comms.ble.register_characteristic('sensor', '19b10001-e8f2-537e-4f6c-d104768a1214', read=True, notify=True)
comms.ble.register_characteristic('wifi', '19b10003-e8f2-537e-4f6c-d104768a1214', read=True, write=True, notify=True, capture=True)

# Register service(s)
comms.ble.register_services()

async def main():
    t1 = asyncio.create_task(comms.ble.sensor_task('sensor', get_random_value))
    t2 = asyncio.create_task(comms.ble.wait_for_connection()) #wait_for_int_write
    t3 = asyncio.create_task(comms.ble.wait_for_str_write('wifi'))
    await asyncio.gather(t1, t2)
asyncio.run(main())

```

### How to install required libraries via mpremote

```sh
# list connected devices
python -m mpremote connect list

# Connect device
python -m mpremote connect COM10

# Install library
python -m mpremote mip install aioble
python -m mpremote mip install asyncio
```