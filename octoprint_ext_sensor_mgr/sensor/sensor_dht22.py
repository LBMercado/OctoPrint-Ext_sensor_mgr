from octoprint_ext_sensor_mgr.sensor.config_property import ConfigProperty
from octoprint_ext_sensor_mgr.sensor.sensor_base import Sensor
from octoprint_ext_sensor_mgr.sensor.sensor_type import SensorType
import Adafruit_DHT
import copy

class DHT22(Sensor):
    _is_config_params_init = False
    
    def __init__(self):
        super().__init__()
        self.sensor_intf = Adafruit_DHT.DHT22
        self.board_pin = None
        self.delay_second = 2
        self.type = SensorType.DHT22
    
    def reset(self):
        super().reset()
    
    @staticmethod
    def config_params(cls=None):
        cls = cls if cls is not None else DHT22
        if not DHT22._is_config_params_init:
            cls._config_params = copy.deepcopy(super(cls, cls).config_params())
            cls._config_params['max_readings'] = ConfigProperty(data_type=type(int), value_list=[], default_value=60)
            cls._config_params['pin'] = ConfigProperty(data_type=type(int), value_list=[], default_value=None)
            cls._config_params['delay_s'] = ConfigProperty(data_type=type(int), value_list=[], default_value=2)
            DHT22._is_config_params_init = True
        return DHT22._config_params
    
    def _configure(self, config: dict):
        self.board_pin = self.convert_value_type(config, 'pin')
        self.delay_second = max(self.convert_value_type(config, 'delay_s'), DHT22.config_params()['delay_s'].default_value)
        self.init_history_reading(self.convert_value_type(config, 'max_readings'))
        is_configured = self.board_pin is not None
        return is_configured
    
    def pin_list(self) -> list:
        return [self.board_pin]
    
    def _read(self):
        res = Adafruit_DHT.read_retry(sensor=self.sensor_intf, pin=self.board_pin, delay_seconds=self.delay_second)
        self._add_reading(res)
        return res
    
    def _write(self):
        pass