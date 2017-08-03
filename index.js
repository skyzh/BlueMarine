require('./hci')()
  .then(() => require('./noble')())
  .then(data_stream => {
    console.log('succeed!')
    data_stream(data => console.log(data));    
  });
  