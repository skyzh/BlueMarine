module.exports = () => new Promise((resolve, reject) => {
  const hci = require('child_process').exec('hciconfig hci0 up');

  hci.on('exit', function() {
    resolve();
  });
})
