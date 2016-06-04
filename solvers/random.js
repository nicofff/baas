var battleship = require("../game")

function randomTile(size){
	var x = Math.floor(Math.random() * size)
	var y = Math.floor(Math.random() * size)
	return [x,y].join("")
}

function validTiles(size){
	var tiles = [];
	for(var x=0;x<size;x++){
		for(var y=0;y<size;y++){
			tiles.push([x,y].join(""))
		}		
	}
	return tiles
}

function pickRandomTile(tiles){
	var ri = Math.floor(Math.random() * tiles.length); // Random Index position in the array
	return tiles.splice(ri, 1)[0];
}

var allTiles = validTiles(10); //TODO don't hardcode size



for (var i = 0; i < 100000; i++) {
	var remainingTiles = allTiles.slice()
	var game = battleship.start();
	var won = false

	var turns = 0
	var moves = []
	while (!won){
		var tile = pickRandomTile(remainingTiles);	
		turns++
		var result = game.playTurn(tile);
		moves.push(tile)
		won = result.code == 3
	
	}

	console.log(turns)

}