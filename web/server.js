var express = require('express');
var cookieParser = require('cookie-parser');
var bodyParser = require('body-parser');
const fs = require('fs');

var app = express();

app.use(bodyParser.json())
app.use(bodyParser.urlencoded({extended: true}))
app.use(cookieParser())

app.use('/static', express.static(__dirname + '/public'));

app.get('/job/:job_id/allimages', (req, res) => {
  var images = [];
  filepath = __dirname + '/public/data/' + req.params.job_id + "/images/";
  fs.readdirSync(filepath).forEach(file => {
    console.log(file);
    images.push(file);
  });
  res.send({ images: images });
});


app.get('/job/:job_id/image/:image_id', function (req, res) {
  var options = {
    root: __dirname + '/public/',
    dotfiles: 'deny',
    headers: {
        'x-timestamp': Date.now(),
        'x-sent': true
    }
  };
  var filepath = '/data/' + req.params.job_id + "/images/" + req.params.image_id;

  res.sendFile(filepath, options);
});

app.get('/job/:job_id/overlay/', function (req, res) {
  var options = {
    root: __dirname + '/public/',
    dotfiles: 'deny',
    headers: {
        'x-timestamp': Date.now(),
        'x-sent': true
    }
  };
  var filepath = '/data/' + req.params.job_id + "/out/overlay.bmp";

  res.sendFile(filepath, options);
});

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
