var express = require('express');
var router = express.Router();

/* GET users listing. */
router.get('/', function(req, res, next) {
  //using https://daveceddia.com/create-react-app-express-backend/ to connect react
  //res.send('respond with a resource');
  res.json([{
      id: 1,
      username: "pathfinder",
  }])

});

module.exports = router;
