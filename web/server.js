var express = require('express');
var cookieParser = require('cookie-parser');
var bodyParser = require('body-parser');

var app = express();

app.use(bodyParser.json())
app.use(bodyParser.urlencoded({extended: true}))
app.use(cookieParser())

app.use('/static', express.static(__dirname + '/public'));

app.get('/job/:job_id/heatmap/', function (req, res) {
  var options = {
    root: __dirname + '/public/',
    dotfiles: 'deny',
    headers: {
        'x-timestamp': Date.now(),
        'x-sent': true
    }
  };
  var filepath = '/data/' + req.params.job_id + "/out/heatmap.bmp";

  res.sendFile(filepath, options);
});

app.listen(4000);

module.exports = app;
