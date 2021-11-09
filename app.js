require('dotenv').config()
var express = require('express');
var app = express();
var exports = module.exports = {};
const LaunchDarkly = require('launchdarkly-node-server-sdk');

const client = LaunchDarkly.init(process.env.LAUNCHDARKLY_SDK_KEY)

const user = {
    "key": "circleci",
  };


function welcomeMessage(){
    var message = "Welcome to CI/CD 101 using CircleCI!";
    return message;
}

// set the view engine to ejs
app.set('view engine', 'ejs');

let showFeature = false
 client.once("ready", () => {
    client.variation("circleci-workshop", user, false,
      (err, sf) => {
        showFeature = sf
        app.get('/', function (req, res) {
            var message = "Welcome to CI/CD 101 using CircleCI & LaunchDarkly!";
            var base_case = "Welcome to CI/CD 101 using CircleCI.";
            res.render("index", {message: showFeature ? message : base_case});
        });
  })
});



client.on('update', () => {
    client.variation("circleci-workshop", user, false,
      (err, sf) => {
        showFeature = sf
  })
  });


var server = app.listen(5000, function () {
    console.log("Node server running...");
});

module.exports = server;
module.exports.welcomeMessage = welcomeMessage;