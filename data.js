const admin = require('firebase-admin');
const debug = require('debug')('blue:data');

const _ = require('lodash');
const report = require('./report');
const CONST = require('./const');

const fb_data = admin.database().ref('/data');

const verify = (chunk) => {
  let _hash = 0;
  for (let i in _.range(CONST.PACKET_SIZE - 2)) {
    _hash = (_hash + chunk[i]) % 255;
  }
  return chunk.readUInt8(CONST.PACKET_SIZE - 1) == _hash + 1;
}

let _data = {};

const process_chunk = (chunk) => {
  if (!verify(chunk)) return false;
  [message_id, response_id, command_id] = [chunk.readUInt16LE(0), chunk.readUInt16LE(2), chunk.readUInt16LE(4)];
  if (_.includes(CONST.COMMAND_PROCESS, command_id)) {
    let value = null;
    if (_.includes(CONST.COMMAND_TYPE.INT, command_id)) value = chunk.readInt32LE(6);
    if (_.includes(CONST.COMMAND_TYPE.FLOAT, command_id)) value = chunk.readFloatLE(6);
    if (!(CONST.COMMAND_STORE[command_id] in _data)) _data[CONST.COMMAND_STORE[command_id]] = [];
    _data[CONST.COMMAND_STORE[command_id]].push(value);
  }
  return true;
};

const do_report = () => {
  let _report = { _length: {} };
  _.forOwn(_data, (v, k) => {
    _report[k] = _.mean(v);
    _report._length[k] = _.size(v);
    if (_.isEmpty(v)) {
      report('error', 'serial', `no data reported`);
      Promise.delay(5000).then(() => {
        process.exit(0);
      });
      return ;
    }
  });
  _report.time = Date.now() / 1000;
  fb_data.push(_report);
  _data = {};
};

module.exports = (data_stream) => new Promise((resolve, reject) => {
  let _interval = setInterval(do_report, 60000);
  let _processor = (function* (buffer) {
    let _buffer = null;
    while (true) {
      let _cnt = 0;
      while (true) {
        let d = yield;
        if (_cnt >= CONST.PACKET_SIZE - 1 && d == 1) break;
        if (d == 0) _cnt++; else _cnt = 0;
      }
      report('success', 'serial', 'connection established');
      
      while (true) {
        let _buf = Buffer.allocUnsafe(CONST.PACKET_SIZE);
        for (let _t in _.range(CONST.PACKET_SIZE)) {
          _buf[_t] = yield;
        }
        debug(_buf, _buf.toString('latin1'));
        if (!process_chunk(_buf)) {
          report('error', 'serial', 'broken packet found');
          break;
        }
      }
    }    
  })();
  data_stream(data => _.forEach(data, d => _processor.next(d)));
});
