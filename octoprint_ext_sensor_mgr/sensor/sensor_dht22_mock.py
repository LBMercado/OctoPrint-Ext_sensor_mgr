from octoprint_ext_sensor_mgr.sensor.sensor_base import Sensor, SensorType
import random

TEMP_RANGE = (32,37)
HUM_RANGE = (60,70)

class DHT22(Sensor):
    def __init__(self):
        super().__init__()
        self.board_pin = None
        self.is_configured = False
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
            temp = random.randint(TEMP_RANGE[0], TEMP_RANGE[1])
            hum = random.randint(HUM_RANGE[0], HUM_RANGE[1])
            ret = (temp, hum)
            self._add_reading(ret)
            return ret
    
    def write(self):
        pass