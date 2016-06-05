var battleship = require("../game")
var _ = require("underscore")


var ships = [{
	name: "Carrier",
	size: 5,
},
{
	name: "Battleship",
	size: 4,
},
{
	name: "Cruiser",
	size: 3,
},
{
	name: "Submarine",
	size: 3,
},
{
	name: "Destroyer",
	size: 2
}];




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

function getMostLikelyTile(allPosiblePositions){
	allPosiblePositions = [].concat.apply([], allPosiblePositions)
	//console.log(allPosiblePositions)
	return _.chain(allPosiblePositions).countBy().pairs().max(_.last).head().value() // Will always return the top-lef-most tile if probability is the same on pmultiple tiles

}

function findAllPosiblePostions(remainingShipsSizes,remainingTiles){
	var posiblePositions = []
	_.each(remainingTiles,function(startTile){
		var tileAvailableVertically = freeTilesDown(startTile,remainingTiles)+1
		var tileAvailableHorizontally = freeTilestoTheRight(startTile,remainingTiles)+1
		_.each(remainingShipsSizes,function(shipSize){
			if (shipSize <= tileAvailableHorizontally){
				posiblePositions.push(shipPlacement(startTile,shipSize,"horizontal"))
			}
			if (shipSize <= tileAvailableVertically){
				posiblePositions.push(shipPlacement(startTile,shipSize,"vertical"))
			}

		});

	});

	return posiblePositions
}

function purgeImposiblePositions(posiblePositions,usedTiles,remainingShipsSizes){

	return _.filter(posiblePositions,function(position){
		if (remainingShipsSizes.indexOf(position.length)===-1){
			return false
		}
		return _.intersection(position,usedTiles).length === 0 
	})
}


function freeTilestoTheRight(tile,remainingTiles){

	if (remainingTiles.indexOf(tile)=== -1) return 0
	var x =parseInt(tile[0])
	var y =parseInt(tile[1])
	for (var newx = x+1 ;newx<10;newx++){
		var newPosition = [newx,y].join("")
		if(remainingTiles.indexOf(newPosition)=== -1){
			return newx-x -1
		}
	}

	return newx-x -1


}

function freeTilesDown(tile,remainingTiles){

	if (remainingTiles.indexOf(tile)=== -1) return 0
	var x =parseInt(tile[0])
	var y =parseInt(tile[1])
	for (var newy = y+1 ;newy<10;newy++){
		var newPosition = [x,newy].join("")
		if(remainingTiles.indexOf(newPosition)=== -1){
			return newy-y -1
		}
	}

	return newy-y -1
}

function shipPlacement(startTile,length,direction="vertical"){
	// asumes the ship fits
	var tiles = []
	var x =parseInt(startTile[0])
	var y =parseInt(startTile[1])
	for (var i = 0;i<length; i++){
		var location = ((direction=="vertical") ? [x,y+i]:[x+i,y]).join("");
		tiles.push(location)
	}

	return tiles;

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
var remainingShipsSizes = _.map(ships,function(ship){return ship.size});

var allPosiblePositions = findAllPosiblePostions(remainingShipsSizes,allTiles)

//console.log(remainingShipPositions)

for (var i = 0; i < 100; i++) {
	var remainingShipsSizes = _.map(ships,function(ship){return ship.size});
	var remainingShipPositions =allPosiblePositions.slice()
	var remainingTiles = allTiles.slice()
	var game = battleship.start();
	var won = false

	var turns = 0
	var moves = []
	var hits = []
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
			//console.log(moves)
			remainingShipPositions = purgeImposiblePositions(remainingShipPositions,moves,remainingShipsSizes)
			var tile = getMostLikelyTile(remainingShipPositions);
			remainingTiles.splice(remainingTiles.indexOf(tile),1)
		}
		//console.log("tile",tile)
		
		
		var result = game.playTurn(tile);
		moves.push(tile)
		//console.log("result",result.message)
		won = result.code == 3
		moves.push(tile)

		if (result.code == 1){
			hits.push(tile)
			var newTargets = generateTargets(remainingTiles,tile)
			targets = _.uniq(targets.concat(newTargets))
			//console.log("new targets",targets);
		}

		if (result.code == 2){
			_.each(ships,function(ship){
				if (result.message == "sunk my "+ship.name){
					remainingShipsSizes.splice(remainingShipsSizes.indexOf(ship.size),1)
				}
			});
		}
	
	}

	console.log(turns)

}