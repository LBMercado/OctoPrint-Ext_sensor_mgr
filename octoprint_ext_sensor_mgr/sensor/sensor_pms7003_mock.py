from octoprint_ext_sensor_mgr.sensor.config_property import ConfigProperty
from octoprint_ext_sensor_mgr.sensor.sensor_base import Sensor
from octoprint_ext_sensor_mgr.sensor.sensor_pms7003 import Pms7003 as Pms7003Actual
from octoprint_ext_sensor_mgr.sensor.sensor_out_type import SensorOutputType
from octoprint_ext_sensor_mgr.sensor.sensor_type import SensorType
from octoprint_ext_sensor_mgr.sensor.util.dev import serial_dev_list
from pms7003 import Pms7003Sensor
import copy

import random

PM2_5_RANGE = (200,300)
PM1_0_RANGE = (100,200)
PM10_RANGE = (300,400)

class Pms7003(Pms7003Actual):
    _is_config_params_init = False
    
    def __init__(self):
        super().__init__()

    def __del__(self):
        pass
    
    def _after_toggle(self):
        pass
    
    def _read(self):
        pm1_0 = random.randint(PM1_0_RANGE[0], PM1_0_RANGE[1])
        pm2_5 = random.randint(PM2_5_RANGE[0], PM2_5_RANGE[1])
        pm10 = random.randint(PM10_RANGE[0], PM10_RANGE[1])
        ret = dict(pm1_0=pm1_0, pm2_5=pm2_5, pm10=pm10)
        
        return ret
    
    def _write(self):
        pass