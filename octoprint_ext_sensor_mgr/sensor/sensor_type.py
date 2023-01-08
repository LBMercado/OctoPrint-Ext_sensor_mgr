# supported sensors
from enum import Enum

class SensorType(Enum):
    NOT_SET = -1
    DHT22 = 1
    

SUPPORTED_SENSOR_LIST = [s for s in SensorType]