// Test whether  ship placement is trully random
var _ = require("underscore");
var battleship = require("./game")

var tilesUsed = {}
var boardsSeen = {}
for (var i = 0; i < 10000; i++) {
	var game = battleship.start();
 	var shipTiles = game.board.map(function(ship){
		return ship.tiles;
	});
	shipTiles = [].concat.apply([], shipTiles)

	var boardId = shipTiles.sort().join(",");
	console.log(boardId);
	/*_.each(shipTiles,function(tile){
		if(tile in tilesUsed){
			tilesUsed[tile]++ 
		}else{
			tilesUsed[tile] = 0
		}
	});*/
}