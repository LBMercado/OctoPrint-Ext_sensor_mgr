"""
  WARNING: This sensor is unreliable due to the tight timing requirements to read it 
  which is what I experienced while testing it on RPi or RPi-like SBCs.
  I recommend using the other temperature sensors 
  (preferrably with standardized communication such as I2C) if possible.
  
  The logic for reading dht22 is copied/adapted from adafruit-circuitpython-dht22
  you can refer to https://github.com/adafruit/Adafruit_CircuitPython_DHT
"""

import array
import time
from octoprint_ext_sensor_mgr.sensor.config_property import ConfigProperty
from octoprint_ext_sensor_mgr.sensor.sensor_base import Sensor
from octoprint_ext_sensor_mgr.sensor.sensor_out_type import SensorOutputType
from octoprint_ext_sensor_mgr.sensor.sensor_type import SensorType
from octoprint_ext_sensor_mgr.sensor.util.dev import gpio_dev_list
import gpiod
import copy

class DHT22(Sensor):
    _is_config_params_init = False
    START_TIME_MS = 100
    READY_COMM_MS = 1.8
    BITBANG_PERIOD_S = 0.25
    
    def __init__(self):
        super().__init__()
        self.last_read_ts = None
        self.type = SensorType.DHT22
        self.output_type =  SensorOutputType.TEMPERATURE | SensorOutputType.HUMIDITY
        self.output_type_unit = None
    
    def reset(self):
        super().reset()
    
    @classmethod
    def config_params(cls):
        if not cls._is_config_params_init:
            cls._config_params = copy.deepcopy(super(DHT22, cls).config_params())
            max_readings_cfg = cls._config_params['max_readings']
            cls._config_params['max_readings'] = ConfigProperty(
                data_type=max_readings_cfg.data_type, value_list=max_readings_cfg.value_list, default_value=60, label=max_readings_cfg.label)
            
            cls._config_params['gpio_device'] = ConfigProperty(data_type=str, value_list=gpio_dev_list(), default_value=None, label='GPIO Device')
            cls._config_params['pin'] = ConfigProperty(data_type=int, value_list=[], default_value=None, label='Pin (WiringPi pin)')
            cls._config_params['delay_s'] = ConfigProperty(data_type=int, value_list=[], default_value=2, label='Delay (in seconds)')
            cls._config_params['ready_comm_s'] = ConfigProperty(data_type=int, value_list=[
            ], default_value=cls.READY_COMM_MS, label='Delay time before ready for communication (in milliseconds)')
            cls._is_config_params_init = True
        return cls._config_params
    
    def output_config(self) -> dict():
        if self.output_type_unit is not None:
            return self.output_type_unit
        
        config = dict()
        if SensorOutputType.TEMPERATURE in self.output_type:
            config['temp'] = dict(type=SensorOutputType.TEMPERATURE.name, unit='C')
        if SensorOutputType.HUMIDITY in self.output_type:
            config['hum'] = dict(type=SensorOutputType.HUMIDITY.name, unit='%')
        self.output_type_unit = config
        
        return config
    
    def _configure(self, config: dict):
        self.board_pin = DHT22.convert_value_type(config, 'pin')
        self.gpio_device = DHT22.convert_value_type(config, 'gpio_device')
        self.delay_second = max(DHT22.convert_value_type(config, 'delay_s'), DHT22.config_params()['delay_s'].default_value)
        self.ready_comm_s = DHT22.convert_value_type(config, 'ready_comm_s')
        self.init_history_reading(DHT22.convert_value_type(config, 'max_readings'))
        if self.board_pin is not None and self.gpio_device is not None:
            is_configured = True
        return is_configured
    
    def _postprc_read(self, reading):
        return dict(temp=reading[0], hum=reading[1]) if reading is not None else None
    
    def _pulses_to_binary(self, pulses: array.array, start: int, stop: int) -> int:
        """Takes pulses, a list of transition times, and converts
        them to a 1's or 0's.  The pulses array contains the transition times.
        pulses starts with a low transition time followed by a high transistion time.
        then a low followed by a high and so on.  The low transition times are
        ignored.  Only the high transition times are used.  If the high
        transition time is greater than __hiLevel, that counts as a bit=1, if the
        high transition time is less that __hiLevel, that counts as a bit=0.
        start is the starting index in pulses to start converting
        stop is the index to convert upto but not including
        Returns an integer containing the converted 1 and 0 bits
        """

        binary = 0
        hi_sig = False
        for bit_inx in range(start, stop):
            if hi_sig:
                bit = 0
                if pulses[bit_inx] > 51:
                    bit = 1
                binary = binary << 1 | bit

            hi_sig = not hi_sig

        return binary

    def _read(self):
        if self.last_read_ts is not None and time.monotonic() - self.last_read_ts <= self.delay_second:
            return None
        self.last_read_ts = time.monotonic()
        res = None
        transitions = []
        pulses = array.array("H")
        # start communication
        chip = gpiod.chip(self.gpio_device)
        line = chip.get_line(self.board_pin)
        req = gpiod.line_request()
        req.consumer = 'sensor_dht22' + str(self.id)
        req.request_type = gpiod.line_request.DIRECTION_OUTPUT
        line.request(req, default_val=1) # pull up default
        start_time_s = DHT22.START_TIME_MS / 1000
        ready_comm_s = self.ready_comm_s / 1000
        
        line.set_value(1)
        time.sleep(start_time_s)
        line.set_value(0)
        time.sleep(ready_comm_s)

        timestamp = time.monotonic()  # take timestamp
        dhtval = True  # start with dht pin true because its pulled up
        line.set_direction_input()

        while time.monotonic() - timestamp < DHT22.BITBANG_PERIOD_S:
            if dhtval != line.get_value():
                dhtval = not dhtval  # we toggled
                transitions.append(time.monotonic())  # save the timestamp
        
        # convert transtions to microsecond delta pulses:
        # use last 81 pulses
        transition_start = max(1, len(transitions) - 81)
        for i in range(transition_start, len(transitions)):
            pulses_micro_sec = int(1000000 * (transitions[i] - transitions[i - 1]))
            pulses.append(min(pulses_micro_sec, 65535))

        new_temperature = 0
        new_humidity = 0

        
        # print(len(pulses), "pulses:", [x for x in pulses])
        if len(pulses) < 10:
            # Probably a connection issue!
            raise RuntimeError("DHT sensor not found, check wiring")

        if len(pulses) < 80:
            # We got *some* data just not 81 bits
            raise RuntimeError("A full buffer was not returned. Try again.")

        buf = array.array("B")
        for byte_start in range(0, 80, 16):
            buf.append(self._pulses_to_binary(pulses, byte_start, byte_start + 16))

        # humidity is 2 bytes
        new_humidity = ((buf[0] << 8) | buf[1]) / 10
        # temperature is 2 bytes
        # MSB is sign, bits 0-14 are magnitude)
        new_temperature = (((buf[2] & 0x7F) << 8) | buf[3]) / 10
        # set sign
        if buf[2] & 0x80:
            new_temperature = -new_temperature
        # calc checksum
        chk_sum = 0
        for b in buf[0:4]:
            chk_sum += b

        # checksum is the last byte
        if chk_sum & 0xFF != buf[4]:
            # check sum failed to validate
            raise RuntimeError("Checksum did not validate. Try again.")

        if new_humidity < 0 or new_humidity > 100:
            # We received unplausible data
            raise RuntimeError("Received unplausible data. Try again.")
        res = (new_temperature, new_humidity)

        return res
    
    def _write(self):
        pass