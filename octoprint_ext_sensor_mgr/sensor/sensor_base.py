from abc import ABC, abstractmethod
from enum import Enum
from collections import deque

# supported sensors
class SensorType(Enum):
    DHT22 = 1

class Sensor(ABC):
    def __init__(self) -> None:
        super().__init__()
        self.init_history_reading()
    
    def init_history_reading(self, max_readings = 1):
        self.max_readings = max_readings
        self.past_readings = deque(maxlen=self.max_readings)
    
    def history_reading_list(self):
        return list(self.past_readings)
    
    def allow_history(self):
        return self.max_readings > 1
    
    def _add_reading(self, reading):
        self.past_readings.append(reading)
    
    def reset(self):
        if self.past_readings is not None:
            self.past_readings.clear()
    
    @abstractmethod
    def configure(self, config):
        pass
    
    @abstractmethod
    def pin_list(self) -> list:
        pass
    
    @abstractmethod
    def type(self) -> SensorType:
        pass
    
    @abstractmethod
    def read(self):
        pass
    
    @abstractmethod
    def write(self):
        pass