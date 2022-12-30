import os
import sys
import time
from octoprint_ext_sensor_mgr.sensor.sensor_dht22_opi import DHT22
from octoprint_ext_sensor_mgr.sensor.sensor_base import SensorType
from octoprint_ext_sensor_mgr.sensor_mngr import SensorManager
from pyA20.gpio import port

DHT_PIN = port.PA6

if __name__ == '__main__':
    test_name = 'Octoprint External Sensor Manager'
    
    print(test_name + ' test script run')
    mngr = SensorManager()
    assert mngr is not None
    
    s1 = DHT22()
    s1.configure({'pin':DHT_PIN})
    assert s1 is not None
    
    lst = mngr.add_sensor(s1)
    ret_item = mngr.sensor_list(SensorType.DHT22)
    print(ret_item)
    
    assert len(ret_item) > 0
    
    ret_sensor = ret_item[0]

    print('dht22 output: ' + str(ret_sensor.read()))
    time.sleep(2)
    ret_sensor.read()
    time.sleep(2)
    ret_sensor.read()

    print('historic readings: ' + str(ret_sensor.history_reading_list()))

    print(test_name + ' passed!')
