/*
 * View model for OctoPrint-Ext_sensor_mgr
 *
 * Author: Luis Mercado
 * License: AGPLv3
 */
$(function() {
    
    function ExtSensorMgrViewModel(parameters) {
        var self = this;

        // injected view models
        self.settingsVM = parameters[0];

        // ko variables
        self.sensorList = ko.observableArray();
        self.selectedSensorId = ko.observable();
        self.sensorTypeList = ko.observableArray();
        self.chartCfgList = ko.observableArray([]);

        // others
        self._do_log = false;
        self.read_frequency_ms = 5000;
        self.selectedSensorChart = null;
        self.BASE_CHART_OPTIONS = {
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: 'second'
                    }
                },
                y: {
                    suggestedMin: 0,
                },
            }
        };

        // functions / methods
        self._log = function (info, obj = undefined) {
            if (self._do_log) {
                console.log("ExtSensorMgrViewModel: " + info);
                if (obj !== undefined) {
                    console.log(obj);
                }
            }
        };

        self.getSensorOutputConfig = function (sensorId) {
            if (!sensorId){
                return;
            }
            return OctoPrint.simpleApiCommand('ext_sensor_mgr', 'sensor_output_config', { 'sensor_id': sensorId});
        };
        
        self.readSensor = function (sensorId) {
            return OctoPrint.simpleApiCommand('ext_sensor_mgr', 'read_sensor', { 'sensor_id': sensorId});
        };

        self.getSensorReadHistoryList = function (sensorId) {
            if (!sensorId){
                return;
            }
            return OctoPrint.simpleApiCommand('ext_sensor_mgr', 'hist_reading_list', { 'sensor_id': sensorId});
        };

        self.sensorTypeFromId = function (sensorTypeId) {
            const sensorType = self.sensorTypeList().filter((type) => {
                return type.value() == sensorTypeId;
            });

            return sensorType.length > 0 ? sensorType[0] : null;
        };

        self._propChartConfig = function (config, datasets, options){
            if (config){
                config.data.datasets.forEach((ds, idx) => {
                    if (datasets[idx]){
                        ds.label = datasets[idx].label;
                        ds.data = datasets[idx].data;
                    }
                });
                options.scales = {...config.options.scales, ...options.scales};
                Object.keys(options).forEach((cfgKey) => {
                    config.options[cfgKey] = { ...config.options[cfgKey], ...options[cfgKey]};
                });
            } else {
                config = {};
                config.data = { datasets: datasets };
                config.options = options;
            }

            return config;
        };
        
        self.ParseSensorToChartConfig = function(sensor, sensorData) {
            var configList = self.chartCfgList();
            
            if (sensor.sensorType.name() == 'DHT22'){
                var chartData = sensorData.map(row => ({...row, timestamp: row.timestamp * 1000})); // js uses millis
                var config, datasets, options;
                
                // temperature
                datasets = [{
                    label: sensor.config.name.value(),
                    data: chartData,
                }];
                options = {
                    ...self.BASE_CHART_OPTIONS,
                    parsing: {
                        xAxisKey: 'timestamp',
                        yAxisKey: 'value.temp',
                    },
                    scales: {
                        ...self.BASE_CHART_OPTIONS.scales,
                        y: {
                            ...self.BASE_CHART_OPTIONS.scales.y,
                            title: {
                                display: true,
                                text: 'Temperature (°C)',
                            },
                            suggestedMax: 100,
                        }
                    }
                };
                config = self._propChartConfig(configList[0], datasets, options);
                if (configList.indexOf(config) == -1){
                    configList.push(config);
                }

                // humidity
                datasets = [{
                    label: sensor.config.name.value(),
                    data: chartData,
                }];
                options = {
                    ...self.BASE_CHART_OPTIONS,
                    parsing: {
                        xAxisKey: 'timestamp',
                        yAxisKey: 'value.hum',
                    },
                    scales: {
                        ...self.BASE_CHART_OPTIONS.scales,
                        y: {
                            ...self.BASE_CHART_OPTIONS.scales.y,
                            title: {
                                display: true,
                                text: 'Humidity (%)',
                            },
                            suggestedMax: 100,
                        }
                    }
                };

                config = self._propChartConfig(configList[1], datasets, options);
                if (configList.indexOf(config) == -1){
                    configList.push(config);
                }
            }

            return configList;
        };

        self.mapSensorOutputStd = function(sensor, config) {
            var outputStd = { ...config };
            
            // add degree symbol ° temperature unit
            var temperatureOutputList = Object.values(outputStd).filter(o => o.type == 'TEMPERATURE');
            self._log(info = 'mapSensorOutputStd: (1) temperatureOutputList: ', obj = temperatureOutputList);

            for (const idx in temperatureOutputList){
                temperatureOutputList[idx].unit = '°' + temperatureOutputList[idx].unit;
            }

            sensor.outputStd = outputStd;
            self._log(info = 'mapSensorOutputStd: (2) sensor output std: ', obj = outputStd);
        };

        self.genSensorOutputObs = function(sensor) {
            var output_list = [];
            const outputStd = sensor.outputStd;

            Object.keys(outputStd).forEach((outputKey) => {
                var readingLabel = outputStd[outputKey].type.toLowerCase();
                readingLabel = readingLabel[0].toUpperCase() + readingLabel.substring(1);
                var reading = {
                    key: outputKey,
                    label: readingLabel,
                    unit: ko.observable(outputStd[outputKey].unit),
                    val: ko.observable()
                };
                output_list.push(reading);
            });

            sensor.output(output_list);
            self._log(info = 'genSensorOutputObs: sensor output: ', obj = sensor.output());
        };

        self.prcSensorReading = function (sensor, reading) {
            if (!reading){
                self._log(info = 'prcSensorReading: no reading returned for sensor', obj = sensor);
                return;
            }
            
            for (const readingKey in reading.value){
                var displ_reading = sensor.output().find(o => o.key == readingKey);
                self._log(info = 'prcSensorReading: (1) displ_reading: ', obj = displ_reading);
                if (displ_reading){
                    displ_reading.val(reading.value[readingKey]);
                }
            }
            self._log(info = 'prcSensorReading: (2) reading: ', obj = reading);
            self._log(info = 'prcSensorReading: (3) output: ', obj = sensor.output());
        };

        // bindings / callbacks
        self.fmtSensorReadingCb = function(unit, value){
            return ko.pureComputed(function() {
                return value() + ' ' + unit();
            });
        };
        
        self.intervalSensorReadCb = function (sensor, sensorId) {
            self.getSensorReadHistoryList(sensorId).done(
                (read_history_list) => {
                    if (!read_history_list) {
                        return;
                    }
                    // dashboard value
                    self.prcSensorReading(sensor, read_history_list.at(-1));

                    // selected sensor graph
                    if (self.selectedSensorId() != sensorId) {
                        return;
                    }
                    const cfg = self.ParseSensorToChartConfig(sensor, read_history_list);
                    self.chartCfgList(cfg);
                    self._log(info = 'initSensorReadingCb (getSensorReadHistoryList): graph config list: ', obj = cfg);

                    self.build_graph(sensorId, cfg);
                });
        };
        
        self.initSensorReadingCb = function (sensorId) {
            var target = self.sensorList().filter((val) => {
                return val.sensorId() == sensorId;
            })[0];
            self._log(info = 'initSensorReadingCb: (1) sensor id: ', obj = sensorId);
            self._log(info = 'initSensorReadingCb: (2) sensor (filtered): ', obj = target);
            target.output = ko.observable();

            var output_config_prom = self.getSensorOutputConfig(sensorId);
            if (output_config_prom) {
                output_config_prom.then((config) => {
                    self.mapSensorOutputStd(target, config);
                    self.genSensorOutputObs(target);
                    self._log(info = 'initSensorReadingCb: (3) sensor: ', obj = target);
                });
            }
        };

        self.build_graph = function (sensorId, configList) {
            sensorId = ko.isObservable(sensorId) ? sensorId() : sensorId;
            if (sensorId === null) {
                return;
            }

            configList.forEach((config, idx) => {
                var data = config.data;
                var options = config.options;
                var chart = config.chart;

                if (chart && chart.data && self.selectedSensorId() == sensorId) {
                    var chartDatasetList = chart.data.datasets;
                    var chartOpt = chart.options;

                    // just update
                    Object.keys(options).forEach((optionKey) => {
                        chartOpt[optionKey] = options[optionKey];
                    });

                    if (chartDatasetList && chartDatasetList.length == 0) {
                        chart.data = { ...data };
                    } else {
                        Object.keys(data.datasets).forEach((datasetKey) => {
                            const newData = data.datasets[datasetKey].data;

                            chartDatasetList[datasetKey].data = newData;
                        });
                    }

                    self._log(info = 'build_graph: update graph data: ', obj = data);

                    chart.update();
                    return;
                }
                self._log(info = 'build_graph: new graph data: ', obj = data);
                const canvas_elem = $('#ext_sensor_mgr_sensor_graph' + idx)[0];

                const cfg = {
                    type: 'line',
                    options: {
                        ...self.BASE_CHART_OPTIONS,
                        ...options
                    },
                    data: { ...data },
                };

                if (chart != undefined) {
                    chart.destroy();
                }
                config.chart = new Chart(canvas_elem, cfg);
            });
        };

        self.resetChart = function() {
            self.chartCfgList([]);
        };
        
        self.onBeforeBinding = function() {
            self._do_log = self.settingsVM.settings.plugins.ext_sensor_mgr.enable_logging();
            self.sensorTypeList(self.settingsVM.settings.plugins.ext_sensor_mgr.supported_sensor_list());
            self.read_frequency_ms = self.settingsVM.settings.plugins.ext_sensor_mgr.read_freq_s() * 1000;
            // deep copy to prevent modification of settings
            var sensorList = self.settingsVM.settings.plugins.ext_sensor_mgr.active_sensor_list();
            sensorList = ko.mapping.fromJS(ko.mapping.toJS(sensorList))();
            sensorList = sensorList.map((s) => (
                {
                    ...s,
                    sensorType: self.sensorTypeFromId(s.sensorType())
                }
            ));
            self.sensorList(sensorList);
            self.sensorList().forEach((val) => {
                self.initSensorReadingCb(val.sensorId());
            });

            self._log(info = 'onBeforeBinding: (1) supported sensor types: ', obj = self.sensorTypeList());
            self._log(info = 'onBeforeBinding: (2) active sensors: ', obj = self.sensorList());
        };

        self.onEventSettingsUpdated = function() {
            self.read_frequency_ms = self.settingsVM.settings.plugins.ext_sensor_mgr.read_freq_s() * 1000;
            // reinitialize without destroying original observables

            self._log(info = 'onEventSettingsUpdated: (1) supported sensor types: ', obj = self.sensorTypeList());
            self._log(info = 'onEventSettingsUpdated: (2) active sensors: ', obj = self.sensorList());
        };

        self.onTabChange = function (next, current) {
            if (next == '#tab_plugin_ext_sensor_mgr') {
                // reset the interval callbacks
                for (const idx in self.sensorList()){
                    var sensor = self.sensorList()[idx];
                    if (!sensor.read_cb)
                        sensor.read_cb = setInterval(() => self.intervalSensorReadCb(sensor, sensor.sensorId()), self.read_frequency_ms);
                }
                self._log(info = 'onTabChange: resetting intervals: ', self.sensorList());
            } else if (current == '#tab_plugin_ext_sensor_mgr') {
                // stop the interval callbacks
                for (const idx in self.sensorList()){
                    const sensor = self.sensorList()[idx];
                    clearInterval(sensor.read_cb);
                    sensor.read_cb = null;
                }
                self._log(info = 'onTabChange: stopping intervals: ', obj = self.sensorList());
            }
        };

    }

    OCTOPRINT_VIEWMODELS.push({
        construct: ExtSensorMgrViewModel,
        dependencies: [ "settingsViewModel" ],
        elements: [ "#tab_plugin_ext_sensor_mgr" ]
    });
});
