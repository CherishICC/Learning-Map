// run node start.js

// import express JS module into app
// and creates its variable.
var cors = require("cors");
var express = require("express");
var app = express();

app.use(cors())
// Creates a server which runs on port 3000 and
// can be accessed through localhost:3000
app.listen(3000, function () {
  console.log("server running on http://127.0.0.1:3000\nView the output on http://localhost:3000/name");
});

// Function callName() is executed whenever
// url is of the form localhost:3000/name
app.get("/name", callName);

function callName(req, res) {
  // Use child_process.spawn method from
  // child_process module and assign it
  // to variable spawn
  var spawn = require("child_process").spawn;

  // Parameters passed in spawn -
  // 1. type_of_script
  // 2. list containing Path of the script
  //    and arguments for the script

  // E.g : http://localhost:3000/name?filename=NIRF.csv
  var process = spawn("python3", ["./script.py", req.query.filename, req.query.resultfile]);


  // Takes stdout data from script which executed
  // with arguments and send this data to res object
  process.stdout.on("data", function (data) {
    res.send(data.toString());
  });
}
