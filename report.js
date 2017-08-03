const admin = require('firebase-admin');

const level_map = {
  'error': 0,
  'info': 1,
  'success': 2
};

const _errors = admin.database().ref('/error');

module.exports = (level, stage, message) => {
  console.log(`${stage}: ${message}`);
  _errors.push({ level: level_map[level], stage, message, time: Date.now() / 1000 }).then(d => null);
};
