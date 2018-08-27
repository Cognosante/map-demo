var express = require('express');
var app = express();
var redis = require('redis');

var redistPort = process.env.REDIS_SERVICE_PORT || 6379;
var redisHost = process.env.REDIS_SERVICE_HOST || 'redis';
var appPort = process.env.APP_PORT || 8080;

var client = redis.createClient(redistPort, redisHost);
client.on('error', function(err) {
  console.error('Redis error', err);
});

app.get('/', function(req, res) {
  res.redirect('/index.html');
});

app.get('/json', function(req, res) {
  client.hlen('wallet', function(err, coins) {
    client.get('hashes', function(err, hashes) {
      var now = Date.now() / 1000;
      res.json({
        coins: coins,
        hashes: hashes,
        now: now
      });
    });
  });
});

app.use(express.static('public'));

var server = app.listen(appPort, function() {
  console.log('web_frontend running on port ' + appPort);
});

module.exports = server;
