from octoprint_ext_sensor_mgr.sensor.sensor_sht30 import Sht30 as Sht30Actual
import random

TEMP_RANGE = (31,37)
HUM_RANGE = (50,70)

class Sht30(Sht30Actual):
    _is_config_params_init = False
    
    def __init__(self):
        super().__init__()
    
    def reset(self):
        super().reset()
    
    def _configure(self, config: dict):
        self.bus_num = Sht30.convert_value_type(config, 'bus')
        self.i2c_addr = Sht30.convert_value_type(config, 'i2c_addr')
        self.init_history_reading(Sht30.convert_value_type(config, 'max_readings'))
        
        is_configured = True
        return is_configured
    
    def _after_toggle(self):
        pass
    
    def _read(self):
        cTemp = random.randint(TEMP_RANGE[0], TEMP_RANGE[1])
        humidity = random.randint(HUM_RANGE[0], HUM_RANGE[1])
        
        return dict(temp=cTemp, hum=humidity)
    
    def _write(self):
        pass