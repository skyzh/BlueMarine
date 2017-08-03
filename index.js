const admin = require('firebase-admin');

const config = {
  credential: admin.credential.cert(require('./config/admin.json')),
  databaseURL: "https://bluesense-9e31b.firebaseio.com"
};

admin.initializeApp(config);

require('./hci')()
  .then(() => require('./noble')())
  .then(data_stream => require('./data')(data_stream));

