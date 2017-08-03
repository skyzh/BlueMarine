module.exports = {
  DEFAULT_TIMEOUT: 15000,
  PACKET_SIZE: 16,
  COMMAND: {
    PM01: 70,
    PM25: 71,
    PM10: 72,
    BME_TEMPERATURE: 100,
    BME_HUMIDITY: 101,
    BME_TEMPERATURE: 105,
  },
  COMMAND_TYPE: {
    INT: [70, 71, 72],
    FLOAT: [100, 101, 105]
  },
  COMMAND_STORE: {
    70: 'pm01',
    71: 'pm25',
    72: 'pm10',
    100: 'tc',
    101: 'hum',
    105: 'pressure'
  },
  COMMAND_PROCESS: [70, 71, 72, 100, 101, 105]
};
