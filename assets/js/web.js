//var millisPerFlip = 2000;
var millisPerFlip = 500;
var nodeRadius = 10;
var nodeColor = "black";
var connColor = "black";
var canvW = 800;
var canvH = 800;
var webMargin = 40;
//var nodes = [];
var nodes = {};
var movies = {};
var connections = [];
var centerText = "";

function getNode (n) {
    return nodes[n.toString()];
}

function initiateWeb(actorList, movieList, connections) {
    initNodes(actorList);
    initMovies(movieList);
    initConnections(connections);
    canvasControl.start();
}

function initNodes (actorList) {
    var len = actorList.length;
    var angleIncrement = (2 * Math.PI) / len;
    var centerX = canvW / 2;
    var centerY = canvH / 2;
    var bigRadX = (canvW - 2 * webMargin) / 2;
    var bigRadY = (canvH - 2 * webMargin) / 2;
    var newNode;
    for (var i = 0; i < len; i++) {
        newNode = new Node(centerX + bigRadX * Math.cos(i * angleIncrement), centerY - bigRadY * Math.sin(i * angleIncrement), nodeRadius, nodeColor, actorList[i][1]);
        nodes[actorList[i][0].toString()] = newNode;
    }
}

function initMovies (movieList) {
    var movie;
    for (var i = 0; i < movieList.length; i++) {
        movie = movieList[i];
        movies[movie[0].toString()] = movie[1];
    }
}

function initConnections (connectionObj) {
    var movieList;
    var twoNodes;
    var node1;
    var node2;
    var conn;
    for (var attr in connectionObj) {
        movieList = connectionObj[attr];
        twoNodes = attr.split(",");
        node1 = parseInt(twoNodes[0]);
        node2 = parseInt(twoNodes[1]);
        conn = new Connection (node1, node2, connColor, movieList);
        connections.push(conn);
    }
}

var canvasControl = {
    canvas : document.createElement("canvas"),
    start : function() {
        this.canvas.width = canvW;
        this.canvas.height = canvH;
        this.context = this.canvas.getContext("2d");
        document.body.insertBefore(this.canvas, document.body.childNodes[0]);
        this.cFrame = 0;
        this.interval = setInterval(flip, millisPerFlip);
        },
    clear : function() {    // blanks canvas.
        this.context.clearRect(0, 0, this.canvas.width, this.canvas.height);
    }
}

function Node (x, y, r, color, name) {
    this.x = x;
    this.y = y;
    this.r = r;  // radius
    this.color = color;
    this.name = name;
    this.draw = function () {   // is ".display" builtin?
        context = canvasControl.context;
        context.beginPath();
        context.arc(x, y, r, 0, 2 * Math.PI);
        context.closePath();
        context.fillStyle = this.color;
        context.fill();
    }
}

function Connection (node1, node2, color, movies) {
    this.node1 = node1;
    this.node2 = node2;
    this.color = color;
    this.movies = movies;
    this.draw = function () {
        context = canvasControl.context;
        context.beginPath();
        context.moveTo(nodes[node1].x, nodes[node1].y);
        context.lineTo(nodes[node2].x, nodes[node2].y);
        context.closePath();
        context.stroke();
    }
    this.getWords = function () {
        var name1 = nodes[node1].name;
        var name2 = nodes[node2].name;
        var baseS = name1 + " and " + name2 + " were both in ";
        var len = this.movies.length;
        if (len == 1) {
            return baseS + movies[0] + ".";
        } else if (len == 2) {
            return baseS + movies[0] + " and " + movies[1] + ".";
        } else {
            var s = baseS;
            for (var i = 0; i < len - 1; i++) {
                s += movies[i] + ", ";
            }
            return s + "and " + movies[len - 1] + ".";
        }

    }
}

function flip() {
    canvasControl.clear();
    for (var attr in nodes) {
        nodes[attr].draw();
    }
    for (var i = 0; i < connections.length; i++) {
        connections[i].draw();
    }
    canvasControl.context.font = "30px Arial";
    canvasControl.context.fillText(centerText, canvW / 2, canvH / 2);
    canvasControl.cFrame += 1;
}


function getMousePos(e) {
    var rect = canvasControl.canvas.getBoundingClientRect();
    return {
        x: e.clientX - rect.left,
        y: e.clientY - rect.top,
    };
}

function dist (x1, y1, x2, y2) {
    return (((x2 - x1) ** 2) + ((y2 - y1) ** 2)) ** 0.5
}

canvasControl.canvas.addEventListener('mousemove', function(e) {
    var mousePos = getMousePos(e);
    var node;
    for (var attr in nodes) {
        node = nodes[attr];
        if (dist(mousePos.x, mousePos.y, node.x, node.y) <= node.r) {
            // console.log(node.name);
            centerText = node.name;
        }
    }
});




