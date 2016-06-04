// Test whether  ship placement is trully random
var _ = require("underscore");
var battleship = require("./game")

var tilesUsed = {}

for (var i = 0; i < 10000; i++) {
	var game = battleship.start();
 	var shipTiles = game.board.map(function(ship){
		return ship.tiles;
	});
	shipTiles = [].concat.apply([], shipTiles)

	_.each(shipTiles,function(tile){
		if(tile in tilesUsed){
			tilesUsed[tile]++ 
		}else{
			tilesUsed[tile] = 0
		}
	});
}

console.log(tilesUsed);