from octoprint_ext_sensor_mgr.sensor.sensor_sht30_mock import Sht30
from octoprint_ext_sensor_mgr.sensor.sensor_qmp6988_mock import Qmp6988
from octoprint_ext_sensor_mgr.sensor.sensor_env3_unit import Env3Unit as Env3UnitActual

class Env3Unit(Env3UnitActual):
    _is_config_params_init = False
    
    def __init__(self):
        super().__init__()
        self.qmp6988: Qmp6988 = Qmp6988()
        self.sht30: Sht30 = Sht30()
    
    def reset(self):
        super().reset()