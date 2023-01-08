from octoprint_ext_sensor_mgr.sensor.config_property import ConfigProperty
from octoprint_ext_sensor_mgr.sensor.sensor_base import Sensor
from octoprint_ext_sensor_mgr.sensor.sensor_out_type import SensorOutputType
from octoprint_ext_sensor_mgr.sensor.sensor_type import SensorType
from octoprint_ext_sensor_mgr.dep.DHT_Python_library_Orange_PI import dht
from pyA20.gpio import gpio
import copy

class DHT22(Sensor):
    _is_config_params_init = False
    
    def __init__(self):
        super().__init__()
        self.sensor_intf = None
        self.board_pin = None
        self.type = SensorType.DHT22
        self.output_type =  SensorOutputType.TEMPERATURE | SensorOutputType.HUMIDITY
        self.output_unit_seq = ('C', '%')
    
    def reset(self):
        super().reset()
    
    @classmethod
    def config_params(cls=None):
        cls = cls if cls is not None else DHT22
        if not cls._is_config_params_init:
            cls._config_params = copy.deepcopy(super(cls, cls).config_params())
            max_readings_cfg = cls._config_params['max_readings']
            cls._config_params['max_readings'] = ConfigProperty(
                data_type=max_readings_cfg.data_type, value_list=max_readings_cfg.value_list, default_value=60, label=max_readings_cfg.label)
            cls._config_params['pin'] = ConfigProperty(data_type=type(int), value_list=[], default_value=None, label='Pin')
            cls._is_config_params_init = True
        return cls._config_params
    
    def output_config(self) -> dict():
        config = dict()
        if SensorOutputType.TEMPERATURE in self.output_type:
            config['temp'] = dict(type=SensorOutputType.TEMPERATURE.name, unit=self.output_unit_seq[0])
        if SensorOutputType.HUMIDITY in self.output_type:
            config['hum'] = dict(type=SensorOutputType.HUMIDITY.name, unit=self.output_unit_seq[1])
        return config
    
    def _configure(self, config: dict):
        self.board_pin = self.convert_value_type(config, 'pin')
        self.init_history_reading(self.convert_value_type(config, 'max_readings'))
        if self.board_pin is not None:
            gpio.init()
            self.sensor_intf = dht.DHT(pin=self.board_pin)
        is_configured = self.board_pin is not None
        return is_configured
    
    def pin_list(self) -> list:
        return [self.board_pin]
    
    def _postprc_read(self, reading):
        return dict(temp=reading[0], hum=reading[1])
    
    def _read(self):
        res = self.sensor_intf.read()
        if not res.is_valid():
            return None
        reading_pair = (res.temperature, res.humidity)
        return reading_pair
    
    def _write(self):
        pass