

var battleship = {}

function placeShips(game_ships,size){
	var ships = game_ships.slice();
	var used = [];
	var shipPlacements = [];
	while (ships.length !==0 ){
		var placement = [];
		var aborted = false;
		var ship = ships.pop();
		var placeVertically = Math.random() > 0.5
		var constrainedStart = Math.round(Math.random()*(size-ship.size));
		var unconstrainedStart = Math.floor(Math.random()*(size));
		for (var i = 0;i<ship.size; i++){
			var location = (placeVertically ? [constrainedStart+i,unconstrainedStart] : [unconstrainedStart,constrainedStart+i]).join("");
			
			if (used.indexOf(location) !==-1){
				aborted = true;
				ships.push(ship);
				break;
			}
			placement.push(location);

		}
		if (!aborted){
			used = used.concat(placement);
			shipPlacements.push({
				name:ship.name,
				tiles:placement,
				state:"alive"
			});
		}
	}

	return shipPlacements;
}

function playTurn(tile){
	game = this;
	if (game.hits.indexOf(tile)!== -1){
		return "Move already played";
	}

	game.hits.push(tile);

	var ret = {code:0,message:"miss"};
	for (var ship of game.board){
		if (ship.tiles.indexOf(tile)!== -1){
			ret = {code:1,message:"hit"};
			var nonHitTiles = ship.tiles.filter(function(tile){
				return game.hits.indexOf(tile) === -1
			});
			if (nonHitTiles == 0){
				ret = {code:2,message:"sunk my "+ship.name};
				ship.state = "sunk"
			}
		}
	}

	remainingShips = game.board.filter(function(ship){
		return ship.state != "sunk"
	});

	if (remainingShips.length == 0){
		ret.code = 3
		ret.message += " You won!"
	}

	return ret;
}


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


battleship.start = function start(){
	var game = {}
	game.placeShips = placeShips;
	game.playTurn  = playTurn;
	var board = game.placeShips(ships,10);
	game.board = board;
	game.hists = [];
	return game;
}

module.exports = battleship