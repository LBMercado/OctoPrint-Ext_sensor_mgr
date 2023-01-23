from enum import Enum
from octoprint_ext_sensor_mgr.sensor.config_property import ConfigProperty
from octoprint_ext_sensor_mgr.sensor.sensor_base import Sensor
from octoprint_ext_sensor_mgr.sensor.sensor_env3_unit import Env3Unit
from octoprint_ext_sensor_mgr.sensor.sensor_env3_unit_mock import Env3Unit as Env3UnitMock
from octoprint_ext_sensor_mgr.sensor.sensor_pms7003 import Pms7003
from octoprint_ext_sensor_mgr.sensor.sensor_pms7003_mock import Pms7003 as Pms7003Mock
from octoprint_ext_sensor_mgr.sensor.sensor_qmp6988 import Qmp6988
from octoprint_ext_sensor_mgr.sensor.sensor_qmp6988_mock import Qmp6988 as Qmp6988Mock
from octoprint_ext_sensor_mgr.sensor.sensor_sht30 import Sht30
from octoprint_ext_sensor_mgr.sensor.sensor_sht30_mock import Sht30 as Sht30Mock
from octoprint_ext_sensor_mgr.sensor.sensor_type import SensorType
from octoprint_ext_sensor_mgr.sensor.sensor_dht22_mock import DHT22 as Dht22Mock
from octoprint_ext_sensor_mgr.sensor.sensor_dht22 import DHT22 as Dht22

from typing import Dict
import copy

        
def determine_sensor_config(sensorType: SensorType, is_test=False):
    cls: Sensor = sensor_cls(sensorType, is_test)
    return cls.config_params()

def sensor_cls(sensorType: SensorType, is_test=False):
    cls: Sensor = None
    cls_mock: Sensor = None
    if sensorType == SensorType.DHT22:
        cls = Dht22
        cls_mock = Dht22Mock
    elif sensorType == SensorType.PMS7003:
        cls = Pms7003
        cls_mock = Pms7003Mock
    elif sensorType == SensorType.SHT30:
        cls = Sht30
        cls_mock = Sht30Mock
    elif sensorType == SensorType.QMP6988:
        cls = Qmp6988
        cls_mock = Qmp6988Mock
    elif sensorType == sensorType.ENV3_UNIT:
        cls = Env3Unit
        cls_mock = Env3UnitMock
    
    if not is_test:
        return cls
    else:
        return cls_mock

def transform_sensor_config(config: Dict[str, ConfigProperty]):
    if config is None:
        return None
    ret_config = copy.deepcopy(config)
    
    for k in ret_config.keys():
        ret_config[k] = ret_config[k]._asdict()
        # handle types to be serializable
        if issubclass(ret_config[k]['data_type'], Enum):
            ret_config[k]['value_list'] = [
                dict(key=e.value, val=e.name) for e in ret_config[k]['value_list']]
            ret_config[k]['default_value'] = dict(key=ret_config[k]['default_value'].value, val=ret_config[k]['default_value'].name)
        
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

