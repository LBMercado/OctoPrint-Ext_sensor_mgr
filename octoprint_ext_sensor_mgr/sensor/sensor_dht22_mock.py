from octoprint_ext_sensor_mgr.sensor.config_property import ConfigProperty
from octoprint_ext_sensor_mgr.sensor.sensor_dht22 import DHT22 as Dht22Actual
import random

TEMP_RANGE = (32,37)
HUM_RANGE = (60,70)

class DHT22(Dht22Actual):
    _is_config_params_init = False
    
    def __init__(self):
        super().__init__()
    
    def reset(self):
        super().reset()
    
    def _read(self):
        temp = random.randint(TEMP_RANGE[0], TEMP_RANGE[1])
        hum = random.randint(HUM_RANGE[0], HUM_RANGE[1])
        ret = (temp, hum)
        
        return ret