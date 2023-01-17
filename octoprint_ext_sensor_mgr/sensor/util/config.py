from octoprint_ext_sensor_mgr.sensor.config_property import ConfigProperty
from octoprint_ext_sensor_mgr.sensor.sensor_base import Sensor
from octoprint_ext_sensor_mgr.sensor.sensor_pms7003 import Pms7003
from octoprint_ext_sensor_mgr.sensor.sensor_pms7003_mock import Pms7003 as Pms7003Mock
from octoprint_ext_sensor_mgr.sensor.sensor_type import SensorType
from octoprint_ext_sensor_mgr.sensor.sensor_dht22_mock import DHT22 as Dht22Mock
from octoprint_ext_sensor_mgr.sensor.sensor_dht22 import DHT22 as Dht22

from typing import Dict
import copy

        
def determine_sensor_config(sensorType: SensorType, is_test=False):
    cls: Sensor = None
    cls_mock: Sensor = None
    if sensorType == SensorType.DHT22:
        cls = Dht22
        cls_mock = Dht22Mock
    elif sensorType == SensorType.PMS7003:
        cls = Pms7003
        cls_mock = Pms7003Mock
    
    if not is_test:
        return cls.config_params()
    else:
        return cls_mock.config_params()

def sensor_cls(sensorType: SensorType, is_test=False):
    if sensorType == SensorType.DHT22:
        if is_test:
            return Dht22Mock
        try:
            return Dht22
        except NameError:
            return None
        
    return None

def transform_sensor_config(config: Dict[str, ConfigProperty]):
    if config is None:
        return None
    ret_config = copy.deepcopy(config)
    
    for k in ret_config.keys():
        ret_config[k] = ret_config[k]._asdict()
        # delete pairs we don't need
        del ret_config[k]['data_type']
    
    return ret_config

def parse_sensor_config(config: Dict[str, dict]):
    if config is None:
        return None
    ret_config = copy.deepcopy(config)
    
    for k in ret_config:
        ret_config[k] = ret_config[k]['value'] if 'value' in ret_config[k] else None
        
    return ret_config

