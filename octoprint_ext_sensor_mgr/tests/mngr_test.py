import os
import sys
from octoprint_ext_sensor_mgr.sensor.sensor_dht22 import DHT22
from octoprint_ext_sensor_mgr.sensor.sensor_base import SensorType
from octoprint_ext_sensor_mgr.sensor_mngr import SensorManager

if __name__ == '__main__':
    test_name = 'Octoprint External Sensor Manager'
    
    print(test_name + ' test script run')
    mngr = SensorManager()
    assert mngr is not None
    
    s1 = DHT22()
    assert s1 is not None
    
    lst = mngr.add_sensor(s1)
    ret_item = mngr.sensor_list(SensorType.DHT22)
    print(ret_item)
    
    assert len(ret_item) > 0
    
    print(test_name + ' passed!')