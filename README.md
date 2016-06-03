Inspired by http://www.datagenetics.com/blog/december32011/

I wanted to try and beat his algorithms, so naturally I needeed a battleship game generator.
So I created one, as an http service, because why not!

Listens on port 8080.

/new -> creates a new game and returns it's ID (game_id)
/turn -> recieves the gameID and the tile you want to hit

Examples:

curl http://localhost:8080/new

{"status":0,"game_id":0}


curl -X POST -H "Content-Type: application/json" http://localhost:8080/turn -d '{"game_id":0,"tile":"50"}'

{"code":,"message":"miss"}


curl -X POST -H "Content-Type: application/json" http://localhost:8080/turn -d '{"game_id":0,"tile":"51"}'

{"code":0,"message":"miss"}


curl -X POST -H "Content-Type: application/json" http://localhost:8080/turn -d '{"game_id":0,"tile":"52"}'

{"code":1,"message":"hit"}


curl -X POST -H "Content-Type: application/json" http://localhost:8080/turn -d '{"game_id":0,"tile":"53"}'

{"code":1,"message":"hit"}


curl -X POST -H "Content-Type: application/json" http://localhost:8080/turn -d '{"game_id":0,"tile":"54"}'

{"code":1,"message":"hit"}


curl -X POST -H "Content-Type: application/json" http://localhost:8080/turn -d '{"game_id":0,"tile":"55"}'

{"code":1,"message":"hit"}


curl -X POST -H "Content-Type: application/json" http://localhost:8080/turn -d '{"game_id":0,"tile":"56"}'

{"code":2,"message":"sunk my Carrier"}


...


curl -X POST -H "Content-Type: application/json" http://localhost:8080/turn -d '{"game_id":0,"tile":"3"}'

{"code":3,"message":"sunk my Submarine You won!"}


The grid is 10x10

Tile name is "XY" where X is X coordinate [0-9] and Y is Y coordinate [0-9]


Return Codes:

0 -> Miss

1 -> Hit

2 -> Sunk

3 -> Game ended



|Type|Size|
|---|---|
|Aircraft Carrier|5|
|Battleship|4|
|Submarine|3|
|Cruiser|3|
|Destroyer|2|

Placement rules:

· Ships cannot overlap

· Ships can be placed one right next to the other
