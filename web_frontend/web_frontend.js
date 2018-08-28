var express = require('express');
var app = express();
var redis = require('redis');

var appPort = process.env.APP_PORT || 8080;

var redisName = (process.env.REDIS_SERVICE || 'REDIS').toUpperCase();
var redistPort = process.env[redisName + '_SERVICE_PORT'] || 6379;
var redisHost = redisName || 'redis';

var client = redis.createClient(redistPort, redisHost);
if (process.env.REDIS_PASSWORD) {
  client.auth(process.env.REDIS_PASSWORD);
}
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
