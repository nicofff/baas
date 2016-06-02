var http = require('http');
const PORT=8080; 

var games = []

//We need a function which handles requests and send response
function handleRequest(request, response){
	var body="";
	request.on('data', function (data) {
        body += data;
    });
    request.on('end', function () {
        try{
            
            if (request.url == "/new"){
                var gameID = games.push(require("./game")) -1
                response.end(JSON.stringify({status: 0, game_id:gameID}));
            }else if (request.url == "/turn"){
                var data =JSON.parse(body);
                game = games[data.game_id];
                response.end(JSON.stringify((game.playTurn(data.tile))));
            }
            
            
        } catch (e){
            console.log(e);
        }
        
    });

}



//Create a server
var server = http.createServer(handleRequest);

//Lets start our server
server.listen(PORT, function(){
    //Callback triggered when server is successfully listening. Hurray!
    console.log("Server listening on: http://localhost:%s", PORT);
});