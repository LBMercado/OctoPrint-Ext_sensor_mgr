from enum import Flag, auto

class SensorOutputType(Flag):
    TEMPERATURE = auto()
    HUMIDITY = auto()