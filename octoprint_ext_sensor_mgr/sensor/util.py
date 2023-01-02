from octoprint_ext_sensor_mgr.sensor.config_property import ConfigProperty
from octoprint_ext_sensor_mgr.sensor.sensor_type import SensorType
from octoprint_ext_sensor_mgr.sensor.sensor_dht22_mock import DHT22 as Dht22Mock
from typing import Dict
import warnings
import copy

try:
    from octoprint_ext_sensor_mgr.sensor.sensor_dht22_opi import DHT22 as Dht22
except ImportError:
    try:
        from octoprint_ext_sensor_mgr.sensor.sensor_dht22 import DHT22 as Dht22
    except ImportError:
        warnings.warn(message='unsupported platform, dht22 will not function correctly', category=ImportWarning)
    
        
def determine_sensor_config(sensorType: SensorType, is_test=False):
    if sensorType == SensorType.DHT22:
        if is_test:
            return Dht22Mock.config_params()
        try:
            return Dht22.config_params()
        except NameError:
            return None
        
    return None

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