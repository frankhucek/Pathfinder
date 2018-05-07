var express = require('express');
var cookieParser = require('cookie-parser');
var bodyParser = require('body-parser');

var app = express();

app.use(bodyParser.json())
app.use(bodyParser.urlencoded({extended: true}))
app.use(cookieParser())

app.use('/static', express.static(__dirname + '/public'));

app.get('/jobid/1', (req, res) => {
  res.send({ images: 'should send images',
              out: 'should send out'});
});

app.listen(4000);

module.exports = app;
