# supported sensors
from enum import Enum

class SensorType(Enum):
    NOT_SET = -1
    DHT22 = 1
    PMS7003 = 2
    SHT30 = 3
    QMP6988 = 4
    ENV3_UNIT = 5
    

SUPPORTED_SENSOR_LIST = [s for s in SensorType]