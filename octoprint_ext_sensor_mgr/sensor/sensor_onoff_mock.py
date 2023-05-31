from octoprint_ext_sensor_mgr.sensor.config_property import ConfigProperty
from octoprint_ext_sensor_mgr.sensor.sensor_onoff import OnOff as OnOffActual
import copy


class OnOff(OnOffActual):
    _is_config_params_init = False

    def __init__(self):
        super().__init__()

    def reset(self):
        super().reset()

    @classmethod
    def config_params(cls):
        if not cls._is_config_params_init:
            cls._config_params = copy.deepcopy(
                super(OnOff, cls).config_params())
            cls._config_params['max_readings'].default_value = 1

            group_seq = ('Sensor Configuration',)

            cls._config_params['gpio_device'] = ConfigProperty(data_type=str, value_list=[
                                                               '/dev/gpio0'], default_value=None, label='GPIO Device', group_seq=group_seq)
            cls._config_params['pin'] = ConfigProperty(data_type=int, value_list=[
            ], default_value=None, label='Pin (WiringPi pin)', group_seq=group_seq)
            cls._config_params['is_active_low'] = ConfigProperty(data_type=bool, value_list=[
                True, False], default_value=False, label='Is active low?', group_seq=group_seq)

            cls._is_config_params_init = True
        return cls._config_params

    def _configure(self, config: dict):
        self.board_pin = OnOff.convert_value_type(config, 'pin')
        self.gpio_device = OnOff.convert_value_type(config, 'gpio_device')
        self.is_active_low = OnOff.convert_value_type(config, 'is_active_low')
        self.init_history_reading(
            OnOff.convert_value_type(config, 'max_readings'))

        is_configured = self.board_pin is not None and self.gpio_device is not None

        return is_configured

    def _after_toggle(self):
        pass

    def _write(self, input_id, value):
        """
        @value: true if on, false if off
        """
        self.is_on = value
