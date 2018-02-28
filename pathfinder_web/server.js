var express = require('express');
var cookieParser = require('cookie-parser');
var bodyParser = require('body-parser');
var graphqlHTTP = require('express-graphql');
var { buildSchema } = require('graphql');
var schema = './data/schema.js'
var { apolloUploadExpress } = require('apollo-upload-server');

var app = express();

app.use(bodyParser.json())
app.use(bodyParser.urlencoded({extended: true}))
app.use(cookieParser())

app.use('/graphql', graphqlHTTP({
  schema: schema,
  rootValue: root,
  graphiql: false,
}));

app.use(
  '/graphql',
  bodyParser.json(),
  apolloUploadExpress(/* Options */),
  graphqlExpress(/* … */)
)

app.listen(4000);

module.exports = app;
