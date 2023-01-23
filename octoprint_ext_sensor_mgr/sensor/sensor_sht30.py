"""
    SHT30 logic adapted from https://github.com/ControlEverythingCommunity/SHT30/blob/master/Python/SHT30.py
"""

from octoprint_ext_sensor_mgr.sensor.config_property import ConfigProperty
from octoprint_ext_sensor_mgr.sensor.sensor_base import Sensor
from octoprint_ext_sensor_mgr.sensor.sensor_out_type import SensorOutputType
from octoprint_ext_sensor_mgr.sensor.sensor_type import SensorType
from smbus import SMBus
import time
import copy

class Sht30(Sensor):
    _is_config_params_init = False
    DFLT_ADDRESS = 0x44
    MEASURE_CMD = 0x2C
    READ_CMD = 0x00
    MEASURE_CONF_REPEAT_CMD = 0x06 # high repeatability measurement configuration
    READ_BYTE_LEN = 6
    
    def __init__(self):
        super().__init__()
        self.type = SensorType.SHT30
        self.output_type =  SensorOutputType.TEMPERATURE | SensorOutputType.HUMIDITY
        self.output_type_unit = None
        self.bus: SMBus = None
    
    def __del__(self):
        pass
    
    def reset(self):
        super().reset()
    
    @classmethod
    def config_params(cls):
        if not cls._is_config_params_init:
            cls._config_params = copy.deepcopy(super(Sht30, cls).config_params())
            
            max_readings_cfg = cls._config_params['max_readings']
            cls._config_params['max_readings'] = ConfigProperty(
                data_type=max_readings_cfg.data_type, value_list=max_readings_cfg.value_list, default_value=60, label=max_readings_cfg.label)
            
            cls._config_params['bus'] = ConfigProperty(data_type=int, value_list=[], default_value=1, label='I2C Bus No.')
            cls._config_params['i2c_addr'] = ConfigProperty(data_type=int, value_list=[], default_value=Sht30.DFLT_ADDRESS, label='I2C Address (in decimal)')
            
            cls._is_config_params_init = True
        return cls._config_params
    
    def output_config(self) -> dict():
        if self.output_type_unit is not None:
            return self.output_type_unit
        
        config = dict()
        if SensorOutputType.TEMPERATURE in self.output_type:
            config['temp'] = dict(type=SensorOutputType.TEMPERATURE.name, unit='C')
        if SensorOutputType.HUMIDITY in self.output_type:
            config['hum'] = dict(type=SensorOutputType.HUMIDITY.name, unit='%')
        self.output_type_unit = config
        
        return config
    
    def _configure(self, config: dict):
        self.bus_num = Sht30.convert_value_type(config, 'bus')
        self.i2c_addr = Sht30.convert_value_type(config, 'i2c_addr')
        self.init_history_reading(Sht30.convert_value_type(config, 'max_readings'))
        
        if self.i2c_addr is not None and self.bus_num is not None:
            self.bus = SMBus(self.bus_num)
        
        is_configured = self.bus is not None
        return is_configured
    
    def _after_toggle(self):
        if self.bus is None:
            return
        
        if not self.enabled:
            self.bus.close()
        else:
            self.bus.open(self.bus_num)
        
    def _postprc_read(self, reading):
        if reading is None:
            return None
        return dict(temp=reading['temp'], hum=reading['hum'])
    
    def _read(self):
        if self.bus is None:
            return
        # Send measurement command, 0x2C(44)
        #		0x06(06)	High repeatability measurement
        self.bus.write_i2c_block_data(self.i2c_addr, Sht30.MEASURE_CMD, [Sht30.MEASURE_CONF_REPEAT_CMD])
        time.sleep(0.5)
        # Read data back from 0x00(00), 6 bytes
        # cTemp MSB, cTemp LSB, cTemp CRC, Humididty MSB, Humidity LSB, Humidity CRC
        data = self.bus.read_i2c_block_data(self.i2c_addr, Sht30.READ_CMD, Sht30.READ_BYTE_LEN)
        
        # Convert the data
        cTemp = ((((data[0] * 256.0) + data[1]) * 175) / 65535.0) - 45
        humidity = 100 * (data[3] * 256 + data[4]) / 65535.0
        
        return dict(temp=cTemp, hum=humidity)
    
    def _write(self):
        pass