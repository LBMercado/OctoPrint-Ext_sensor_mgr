/*
 * View model for OctoPrint-Ext_sensor_mgr_settings
 *
 * Author: Luis Mercado
 * License: AGPLv3
 */
$(function () {
    function ExtSensorMgrSettingsViewModel(parameters) {
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
                    self._log(info = 'selectedSupportedConfigList ko computed: given config for key = ' + val, obj = config);
                    return {
                        'param': val,
                        'type': config[val].value_list.length > 0 ? self.CONFIG_DATA_TYPE.Options : self.CONFIG_DATA_TYPE.Text,
                        'label': config[val].label,
                    };
                });
            } else {
                return [];
            }
        }, self);

        // others
        self._null_sensor_type = null;
        self.do_subst_mock_sensor = false;
        self._do_log = true;
        self.CONFIG_DATA_TYPE = {
            Text: 1,
            Options: 2
        };

        // functions / methods
        self.toggleSensorButtonCss = function (data) {
            self._log(info = 'toggleSensorButtonCss: enabled = ' + data.enabled());
            return {
                'fa': true,
                'fa-toggle-on': data.enabled(),
                'fa-toggle-off': !data.enabled(),
            };
        };

        self.toggleSensor = function (data) {
            data.enabled(!data.enabled());
            self._log(info = 'toggleSensor: new enabled =' + data.enabled());
        };

        self.addSensor = function () {
            var sensor = {
                'sensorType': ko.observable(self._null_sensor_type), 'enabled': ko.observable(false),
                'sensorId': ko.observable(), 'config': { 'name': { 'value': ko.observable('New Sensor') } }
            };
            self.sensorList.push(sensor);
            self._log(info = 'addSensor: (1) new sensor = ' + sensor);
            self._log(info = 'addSensor: (2) sensor count = ' + self.sensorList().length);
        };

        self.removeSensor = function (data) {
            self._log(info = 'remove sensor', obj = data);
            self.sensorList.remove(data);
            if (self.selectedSensor() == data) {
                self.selectedSensor(null);
            }
            self._log(info = 'removeSensor: sensor count = ' + self.sensorList().length);
        };

        self.isSelectedSensorCb = function (data) {
            return ko.pureComputed(function () {
                return data == self.selectedSensor();
            }, self);
        };

        self.matchingParamConfigCb = function (supp_config, sensorConfig) {
            return ko.computed(function () {
                self._log(info = 'matchingParamConfigCb: (1) supp_config = ', obj = supp_config);
                self._log(info = 'matchingParamConfigCb: (2) sensorConfig = ', obj = sensorConfig);
                if (supp_config.type == sensorConfig[supp_config.param].type()){
                    return sensorConfig[supp_config.param];
                }
                return null;
            }, self);
        };

        self.init_config_param = function (config_param, value = null) {
            config_param.value = value;
            config_param.type = config_param.value_list.length > 0 ? self.CONFIG_DATA_TYPE.Options : self.CONFIG_DATA_TYPE.Text;

            for (const param in config_param){
                config_param[param] = ko.observable(config_param[param]);
            }
        };

        self.prop_sensor_config = function (sensor, supportedConfig) {
            if (!supportedConfig){
                return;
            }
            config = null;

            self._log(info = 'prop_sensor_config: supported config list', obj = supportedConfig);
            self._log(info = 'prop_sensor_config: prop to sensor', obj = sensor);

            if (!sensor.hasOwnProperty('config')) {
                sensor.config = {...supportedConfig};
                config = sensor.config;
                self._log(info = 'prop_sensor_config: new config list', obj = config);
                for (const k in config) {
                    self.init_config_param(config[k]);
                }
            } else {
                config = sensor.config;
                for (const k in supportedConfig) {
                    item = {...supportedConfig[k]};
                    self.init_config_param(item, config.hasOwnProperty(k) ? config[k].value() : null);
                    config[k] = item;
                }
            }
            self.selectedSupportedConfig(supportedConfig);
            self._log(info = 'prop_sensor_config: config list ko computed', obj = self.selectedSupportedConfigList());
            self._log(info = 'prop_sensor_config: processed config list', obj = config);
        };

        self.mdfSensor = function () {
            var sensor = self.selectedSensor();
            self._log(info = 'configure sensor', obj = sensor);
            if (sensor){
                self.getCommandParamList(sensor.sensorType())
                    .done((res) => {
                        self._log(info = 'API command config param list for sensor result', obj = res);
                        self.prop_sensor_config(sensor, res);
                        self._log(info = 'Modify sensor post:  ', obj = sensor);
                        $("#SensorManagerConfigure").modal("show");
                    });
            }
        };

        self.getCommandParamList = function (sensorTypeKey) {
            return OctoPrint.simpleApiCommand('ext_sensor_mgr', 'config_param_list', { 'sensor_type_id': sensorTypeKey});
        };

        self.onSensorTypeChange = function (sensor) {
            if (sensor) {
                // wipe existing config
                sensor.config = { 'name': sensor.config.name };

                self.getCommandParamList(sensor.sensorType())
                    .done((res) => {
                        self.prop_sensor_config(sensor, res);
                    });
            }
        };

        self.enableSensorCb = function (sensor) {
            return ko.pureComputed(() => {
                return sensor() && sensor().sensorType() != self._null_sensor_type.value();
            });
        };

        self.disableSensorConfigCb = function (sensor) {
            return ko.pureComputed(() => {
                if (!ko.isObservable(sensor) || !sensor()){
                    return true;
                }

                return sensor().sensorType() == self._null_sensor_type.value();
            });
        };

        self.onSelectSensor = function (data) {
            self.selectedSensor(data);
            self._log(info = 'onSelectSensor: selected sensor', obj = data);
        };
        
        self.onBeforeBinding = function () {
            self._do_log = self.settingsVM.settings.plugins.ext_sensor_mgr.enable_logging();
            self.do_subst_mock_sensor = self.settingsVM.settings.plugins.ext_sensor_mgr.is_mock_test();
            
            var sensorList = self.settingsVM.settings.plugins.ext_sensor_mgr.active_sensor_list();
            self.sensorList(sensorList);
            self._log(info = 'onBeforeBinding: active sensors: ', obj = self.sensorList());
            sensorList = self.settingsVM.settings.plugins.ext_sensor_mgr.supported_sensor_list();
            self.supportedSensorList(sensorList);
            self._null_sensor_type = self.supportedSensorList().filter((val) => {
                return val.value() == -1;
            })[0];
            self._log(info = 'onBeforeBinding: null sensor defined as: ', obj = self._null_sensor_type);
            self._log(info = 'onBeforeBinding: supported sensors: ', obj = self.supportedSensorList());
        };

        self.onSettingsBeforeSave = function () {
            self._log(info = 'onSettingsBeforeSave: old active sensors: ', obj = self.settingsVM.settings.plugins.ext_sensor_mgr.active_sensor_list());
            self._log(info = 'onSettingsBeforeSave: new active sensors: ', obj = self.sensorList());
            self.settingsVM.settings.plugins.ext_sensor_mgr.active_sensor_list(self.sensorList());
        };

        self._log = function (info, obj = undefined) {
            if (self._do_log) {
                const dbg = "ExtSensorMgrSettingsViewModel: " + info;
                
                if (obj !== undefined) {
                    console.log(dbg + " %o", obj);
                } else {
                    console.log(dbg);
                }
            }
        };
    }

    OCTOPRINT_VIEWMODELS.push({
        construct: ExtSensorMgrSettingsViewModel,
        dependencies: ["settingsViewModel"],
        elements: ["#settings_plugin_ext_sensor_mgr"]
    });
});
