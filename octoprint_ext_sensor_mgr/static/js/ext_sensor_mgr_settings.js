/*
 * View model for OctoPrint-Ext_sensor_mgr_settings
 *
 * Author: Luis Mercado
 * License: AGPLv3
 */
$(function () {
    function Ext_sensor_mgrSettingsViewModel(parameters) {
        var self = this;

        // injected view models
        self.settingsVM = parameters[0];

        // ko variables
        self.sensorList = ko.observableArray();
        self.supportedSensorList = ko.observableArray();
        self.selectedSensor = ko.observable(null); 
        self.selectedSupportedConfig = ko.observable();
        self.selectedSupportedConfigList = ko.computed(function () {
            config = self.selectedSupportedConfig();
            if (config) {
                return Object.keys(config).map((val) => {
                    self._log(info = 'selectedSupportedConfigList ko computed: given config for key = ' + val, obj = config, enable = self._do_log);
                    return {
                        'param': val,
                        'type': config[val].value_list.length > 0 ? self._configDataType.Options : self._configDataType.Text,
                        'label': null, // TODO
                    };
                });
            } else {
                return []
            };
        }, self);

        // others
        self._null_sensor_type = null;
        self.do_subst_mock_sensor = false
        self._do_log = true;
        self._configDataType = {
            Text: 1,
            Options: 2
        };

        // functions / methods
        self.toggleSensorButtonCss = function (data) {
            self._log(info = 'toggleSensorButtonCss: enabled = ' + data.enabled(), enable = self._do_log);
            return {
                'fa': true,
                'fa-toggle-on': data.enabled(),
                'fa-toggle-off': !data.enabled(),
            };
        };

        self.toggleSensor = function (data) {
            data.enabled(!data.enabled());
            self._log(info = 'toggleSensor: new enabled =' + data.enabled(), enable = self._do_log);
        };

        self.addSensor = function () {
            var sensor = { 'sensorType': ko.observable(self._null_sensor_type), 'enabled': ko.observable(false), 'sensorId': ko.observable(true) };
            self.sensorList.push(sensor);
            self._log(info = 'addSensor: sensor count = ' + self.sensorList().length, enable = self._do_log);
        };

        self.removeSensor = function (data) {
            self._log(info = 'remove sensor', obj = data, enable = self._do_log);
            self.sensorList.remove(data);
            if (self.selectedSensor() == data) {
                self.selectedSensor(null);
            }
            self._log(info = 'removeSensor: sensor count = ' + self.sensorList().length, enable = self._do_log);
        };

        self.isSelectedSensorCb = function (data) {
            return ko.pureComputed(function () {
                return data == self.selectedSensor();
            }, self);
        };

        self.matchingParamConfigCb = function (supp_config, sensorConfig) {
            return ko.computed(function () {
                self._log(info = 'matchingParamConfigCb: (1) supp_config = ', obj = supp_config, enable = self._do_log);
                self._log(info = 'matchingParamConfigCb: (2) sensorConfig = ', obj = sensorConfig, enable = self._do_log);
                if (supp_config.type == sensorConfig[supp_config.param].type()){
                    return sensorConfig[supp_config.param];
                }
                return null;
            }, self);
        };

        self.init_config_param = function (config_param, value = null) {
            config_param['value'] = value;
            config_param['type'] = config_param.value_list.length > 0 ? self._configDataType.Options : self._configDataType.Text;

            for (param in config_param){
                config_param[param] = ko.observable(config_param[param]);
            }
        };

        self.prop_sensor_config = function (sensor, supportedConfig) {
            if (!supportedConfig){
                return;
            };
            config = null;

            self._log(info = 'prop_sensor_config: supported config list', obj = supportedConfig, enable = self._do_log);
            self._log(info = 'prop_sensor_config: prop to sensor', obj = sensor, enable = self._do_log);

            if (!sensor.hasOwnProperty('config')) {
                sensor['config'] = {...supportedConfig};
                config = sensor.config;
                self._log(info = 'prop_sensor_config: new config list', obj = config, enable = self._do_log);
                for (k in config) {
                    self.init_config_param(config[k]);
                }
            } else {
                config = sensor.config;
                for (k in supportedConfig) {
                    item = {...supportedConfig[k]}
                    self.init_config_param(item, config.hasOwnProperty(k) ? config[k].value() : null)
                    config[k] = item;
                };
            };
            self.selectedSupportedConfig(supportedConfig);
            self._log(info = 'prop_sensor_config: config list ko computed', obj = self.selectedSupportedConfigList(), enable = self._do_log);
            self._log(info = 'prop_sensor_config: processed config list', obj = config, enable = self._do_log);
        };

        self.mdfSensor = function () {
            var sensor = self.selectedSensor()
            self._log(info = 'configure sensor', obj = sensor, enable = self._do_log);
            if (sensor){
                self.getCommandParamList(sensor.sensorType())
                    .done((res) => {
                        self._log(info = 'API command config param list for sensor result', obj = res, enable = self._do_log);
                        self.prop_sensor_config(sensor, res);
                        self._log(info = 'Modify sensor post:  ', obj = sensor, enable = self._do_log);
                        $("#SensorManagerConfigure").modal("show");
                    });
            };
        };

        self.getCommandParamList = function (sensorTypeKey) {
            return OctoPrint.simpleApiCommand('ext_sensor_mgr', 'config_param_list', { 'sensor_type_id': sensorTypeKey});
        };

        self.onSelectSensor = function (data) {
            self.selectedSensor(data);
            self._log(info = 'selected sensor', obj = data, enable = self._do_log);
        };
        
        self.onBeforeBinding = function () {
            self._do_log = self.settingsVM.settings.plugins.ext_sensor_mgr.enable_logging();
            self.do_subst_mock_sensor = self.settingsVM.settings.plugins.ext_sensor_mgr.is_mock_test();
            
            var sensorList = self.settingsVM.settings.plugins.ext_sensor_mgr.active_sensor_list();
            self.sensorList(sensorList);
            self._log(info = 'onBeforeBinding: active sensors: ', obj = self.sensorList(), enable = self._do_log);
            sensorList = self.settingsVM.settings.plugins.ext_sensor_mgr.supported_sensor_list();
            self.supportedSensorList(sensorList);
            self._null_sensor_type = self.supportedSensorList().filter((val) => {
                return val.value() == -1
            })[0];
            self._log(info = 'onBeforeBinding: null sensor defined as: ', obj = self._null_sensor_type, enable = self._do_log);
            self._log(info = 'onBeforeBinding: supported sensors: ', obj = self.supportedSensorList(), enable = self._do_log);
        };

        self.onSettingsBeforeSave = function () {
            self._log(info = 'onSettingsBeforeSave: old active sensors: ', obj = self.settingsVM.settings.plugins.ext_sensor_mgr.active_sensor_list(), enable = self._do_log);
            self._log(info = 'onSettingsBeforeSave: new active sensors: ', obj = self.sensorList(), enable = self._do_log);
            self.settingsVM.settings.plugins.ext_sensor_mgr.active_sensor_list(self.sensorList());
        };

        self._log = function (info, obj = undefined, enable = false) {
            if (enable) {
                console.log(info);
                if (obj !== undefined) {
                    console.log(obj);
                }
            }
        };
    }

    /* view model class, parameters for constructor, container to bind to
     * Please see http://docs.octoprint.org/en/master/plugins/viewmodels.html#registering-custom-viewmodels for more details
     * and a full list of the available options.
     */
    OCTOPRINT_VIEWMODELS.push({
        construct: Ext_sensor_mgrSettingsViewModel,
        // ViewModels your plugin depends on, e.g. loginStateViewModel, settingsViewModel, ...
        dependencies: ["settingsViewModel"],
        // Elements to bind to, e.g. #settings_plugin_ext_sensor_mgr, #tab_plugin_ext_sensor_mgr, ...
        elements: ["#settings_plugin_ext_sensor_mgr"]
    });
});
