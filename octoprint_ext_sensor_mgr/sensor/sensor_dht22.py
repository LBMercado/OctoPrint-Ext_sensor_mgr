from octoprint_ext_sensor_mgr.sensor.sensor_base import Sensor, SensorType
import Adafruit_DHT

class DHT22(Sensor):
    def __init__(self):
        super().__init__()
        self.sensor_intf = Adafruit_DHT.DHT22
        self.board_pin = None
        self.is_configured = False
        self.delay_second = 2
        self.type = SensorType.DHT22
    
    def reset(self):
        super().reset()
    
    def configure(self, config: dict):
        self.board_pin = config['pin'] if 'pin' in config else None
        self.delay_second = max(config['delay_s'], 2) if 'delay_s' in config else 2
        self.init_history_reading(config['max_readings'] if 'max_readings' in config else 60)
        self.is_configured = self.board_pin is not None
    
    def pin_list(self) -> list:
        return [self.board_pin]
    
    def type(self) -> SensorType:
        return self.type
    
    def read(self):
        if self.is_configured:
            res = Adafruit_DHT.read_retry(sensor=self.sensor_intf, pin=self.board_pin, delay_seconds=self.delay_second)
            self._add_reading(res)
            return res
    
    def write(self):
        pass