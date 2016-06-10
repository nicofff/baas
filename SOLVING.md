First of all disclaimers:

· I'm not a computer scientist, I'm a systems engineer. If you are hoping for cool math, you are in the wrong place. 
· This asumes the rules in the README
· There is a factor of game theory to playing this game. If you know the algorithm you are playing against, you are going to place your ships accordingly.
This asumes the ships are placed completely random.

The solutions cited in the README, plus most I was able to find went the route of trying to estimate how many ships could posible be in a tile and derive the probability from there.

The proper way of calculating the probabilities for the ramaining tiles would be to have a list of all posible games with the given miss / hists. 

So naturally, I though that this wasn't being used because the amount of posible games is huge. 
The follow up question was "How huge?".

I don't know if there is a proper way of calculating how many posible games are there. But we can put an upper bound to it.

For the Aircraft Carrier (Size 5) there are 6 ways to place it in a 1x10 grid (0-4,1-5,2-6,3-7,4-8,5-9).
From there you get the total ammount of positions the Aircraft Carrier can be by multipling by 20 (10 rows + 10 columns)

The totals for every ship are:

Aircraft Carrier => 6*20 = 120

Battleship => 7*20 = 140

Submarine => 8*20 = 160

Cruiser	=> 8*20 = 160

Destroyer => 9*20 = 180


If we consider a complete board as the "sum" of one board of each type of ship. Then we get 120*140*160*160*180 posible boards = 77414400000 = 7.7E10

That's a lot to calculate on every turn (even if the real value is a couple orders of magnitude less), but at 100 bits per board that's 7.7E12 bits or 900 GB which is within the realm of what can be precomputed and stored.


Let's say we precompute all the boards and store it to disk. Then, on every turn we can get the current state of the board and compare it to each of the posible boards:

1) If the boards are incompatible (eg: there is a miss were our board has a hit, or viceversa) we ignore it
2) For every tile of the board, we count how many ships were there accross all compatible boards
3) We choose the tile with the highest count


While this might seem impractical, due to the sheer size of the dataset to analyse on each turn, consider that this algorithm is highly paralelizable. The data can be distributed across many nodes and each one can calculate steps 1 and 2 on their own and send to the master node their partial totals. 

Another aproach could be to use gpu's to do the computations and greatly accelerate the process


TODO: 

1) Create the dataset. And get the number of all posible battleship games in the process
2) Solve some games :D

