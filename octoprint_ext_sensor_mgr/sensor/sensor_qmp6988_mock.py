from octoprint_ext_sensor_mgr.sensor.sensor_qmp6988 import Qmp6988 as Qmp6988Actual
import random

TEMP_RANGE = (31, 34)
PSR_RANGE = (1010, 1016)


class Qmp6988(Qmp6988Actual):
    _is_config_params_init = False

    def __init__(self):
        super().__init__()

    def reset(self):
        super().reset()

    def _configure(self, config: dict):
        self.bus_num = Qmp6988.convert_value_type(config, 'bus_num')
        self.i2c_addr = Qmp6988.convert_value_type(config, 'i2c_addr')
        self.temp_sampling = Qmp6988.convert_value_type(
            config, 'temp_sampling')
        self.psr_sampling = Qmp6988.convert_value_type(config, 'psr_sampling')
        self.filter = Qmp6988.convert_value_type(config, 'filter')
        self.pow_mode = Qmp6988.convert_value_type(config, 'pow_mode')

        self.init_history_reading(
            Qmp6988.convert_value_type(config, 'max_readings'))

        is_configured = True
        return is_configured

    def _after_toggle(self):
        pass

    def _postprc_read(self, reading):
        if reading is None:
            return None
        return dict(temp=reading['temperature'], psr=reading['pressure'])

    def _read(self):
        cTemp = random.randint(TEMP_RANGE[0], TEMP_RANGE[1])
        psr = random.randint(PSR_RANGE[0], PSR_RANGE[1])

        return dict(temperature=cTemp, pressure=psr)
