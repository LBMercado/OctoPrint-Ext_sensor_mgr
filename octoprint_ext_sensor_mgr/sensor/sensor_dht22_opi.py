from octoprint_ext_sensor_mgr.sensor.sensor_base import Sensor, SensorType
from octoprint_ext_sensor_mgr.dep.DHT_Python_library_Orange_PI import dht
from pyA20.gpio import gpio

class DHT22(Sensor):
    def __init__(self):
        super().__init__()
        self.sensor_intf = None
        self.board_pin = None
        self.is_configured = False
        self.type = SensorType.DHT22
    
    def reset(self):
        super().reset()
    
    def configure(self, config: dict):
        self.board_pin = config['pin'] if 'pin' in config else None
        self.init_history_reading(config['max_readings'] if 'max_readings' in config else 60)
        if self.board_pin is not None:
            gpio.init()
            self.sensor_intf = dht.DHT(pin=self.board_pin)
        self.is_configured = self.board_pin is not None
    
    def pin_list(self) -> list:
        return [self.board_pin]
    
    def type(self) -> SensorType:
        return self.type
    
    def read(self):
        if self.is_configured:
            res = self.sensor_intf.read()
            if not res.is_valid():
                return None
            reading_pair = (res.temperature, res.humidity)
            self._add_reading(reading_pair)
            return reading_pair
    
    def write(self):
        pass