var battleship = require("../game")
var _ = require("underscore")
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

function pickRandomParTile(tiles){
	while(true){
		var ri = Math.floor(Math.random() * tiles.length); // Random Index position in the array
		var tile = tiles[ri]
		if ((parseInt(tile[0])+parseInt(tile[1]))%2 == 0){
			return tiles.splice(ri, 1)[0];
		}
	}
}


function pickTile(remaining,played){
	
}

function generateTargets(remainingTiles,lastTile){ //TODO: Make tiles an array instead of string, otherwise this will be a pain
	var x =parseInt(lastTile[0])
	var y =parseInt(lastTile[1])
	var targets = [[x-1,y],[x+1,y],[x,y-1],[x,y+1]].map(function(e){return e.join("")})
	return targets.filter(function(target){
		return remainingTiles.indexOf(target)!== -1
	});

}

var allTiles = validTiles(10); //TODO don't hardcode size

for (var i = 0; i < 100000; i++) {
	var remainingTiles = allTiles.slice()
	var game = battleship.start();
	var won = false

	var turns = 0
	var moves = []
	var targets = []
	var targetMode = false
	while (!won && turns < 100){
		turns++
		targetMode = targets.length > 0
		//console.log(targetMode?"target":"hunt")

		
		if (targetMode){
			var tile = pickRandomTile(targets)
			remainingTiles.splice(remainingTiles.indexOf(tile),1)
		}else{
			var tile = pickRandomParTile(remainingTiles);	
		}
		//console.log("tile",tile)
		
		
		var result = game.playTurn(tile);
		//console.log("result",result.message)
		won = result.code == 3
		moves.push(tile)

		if (result.code == 1){
			var newTargets = generateTargets(remainingTiles,tile)
			targets = _.uniq(targets.concat(newTargets))
			//console.log("new targets",targets);
		}
	
	}

	console.log(turns)

}