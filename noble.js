const _ = require('lodash');
const Promise = require('bluebird');
const noble = require('noble');
const CONST = require('./const');
const report = require('./report');

Promise.promisifyAll(require('noble/lib/peripheral').prototype);
Promise.promisifyAll(require('noble/lib/service').prototype);
Promise.promisifyAll(require('noble/lib/characteristic').prototype);
Promise.promisifyAll(require('noble/lib/descriptor').prototype);

const UUID = {
  characteristics: {
    'dfb1': 'serial_port',
    'dfb2': 'command',
  },
  mac: 'c4be841bba85'
};

module.exports = () => new Promise((resolve, reject) => {
  let _characteristics = {};

  noble.on('stateChange', state => {
    if (state === 'poweredOn') noble.startScanning();
  });

  noble.on('discover', peripheral => {
    peripheral.on('disconnect', err => {
      report('error', 'bluetooth', `disconnected`);
      Promise.delay(5000).then(() => {
        process.exit(0);
      });
    });
    if (peripheral.uuid == UUID.mac) {
      report('info', 'bluetooth', `device ${UUID.mac} discovered`);
      noble.stopScanning();
      peripheral.connectAsync().timeout(CONST.DEFAULT_TIMEOUT)
        .then(() => {
          report('info', 'bluetooth', `connected`);
          return peripheral.discoverServicesAsync([]).timeout(CONST.DEFAULT_TIMEOUT);
        })
        .then(services => {
          report('info', 'bluetooth', `service discovered`);
          _.forEach(services, service => {
            service.discoverCharacteristicsAsync([]).timeout(CONST.DEFAULT_TIMEOUT).then(characteristics => {
              _.forEach(characteristics, characteristic => {
                if (characteristic.uuid in UUID.characteristics) {
                  _characteristics[UUID.characteristics[characteristic.uuid]] = characteristic;
                  if (_characteristics.serial_port && _characteristics.command) {
                    report('info', 'bluetooth', `serial characteristic discovered`);
                    _characteristics.serial_port.subscribe(err => null);

                    resolve((cb) => {
                      _characteristics.serial_port.on('data', cb);
                    });

                    return false;
                  }
                }
              });
            });
          });
        });
    }
  });
});
