from octoprint_ext_sensor_mgr.sensor.sensor_base import Sensor, SensorType

class SensorManager:
    def __init__(self):
        self._sensor_list = []
        
    def add_sensor(self, sensor: Sensor):
        if sensor not in self._sensor_list:
            self._sensor_list.append(sensor)
    
    def remv_sensor(self, sensor: Sensor):
        if sensor in self._sensor_list:
            self._sensor_list.remove(sensor)
    
    def is_pin_used(self, pin):
        return any(pin in s.pin_list() for s in self._sensor_list)
    
    def sensor_list(self, sensor_type: SensorType = None):
        if sensor_type is None:
            return self._sensor_list
        return list(filter(lambda s: s.type == sensor_type, self._sensor_list))