This file contains a description of my advances towards trying to generate a better battleship algorithm. I'm writing this as documentation if I manage to solve this, or as a starting guide for enyone else who wants to get a shot at this.


First of all disclaimers:

· I'm not a computer scientist, I'm a systems engineer. If you are hoping for cool math, you are in the wrong place. 

· This asumes the rules in the README

· There is a factor of game theory to playing this game. If you know the algorithm you are playing against, you are going to place your ships accordingly. This asumes the ships are placed completely random.

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


If we consider a complete board as the "sum" of one board of each type of ship. Then we get 120x140x160x160x180 posible boards = 77414400000 = 7.7E10

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

UPDATE 1:

I got a generator working. It would probably take 10 hours just to count all available games. Ain't nobody got time for that. Besides, I ctrl+c'd it by mistake after an hour or so

What did I learn from that?

Well, the couple orders of magnitude drop I was hoping for between my upper bound and the valid boards was more like a 60% drop, so we are looking to something like 400GB to store all posible games.

In the spirit of creating a faster generator I taught myself some opencl and put togheter a generator that uses a gpu to paralelize the board testing

UPDATE 2:

Who would have thought that gpu computing was hard! \s

As of now, the opencl generator is about 20% faster than single core cpu generator. I'm quite happy at the optimizations I've made to make the problem as paralelizable as posible, yet it seems I need to teach me some more opencl optimizations.

It really sucks there doesn't seem to be much in the way of profiling for gpu's using opencl. Looks like I might have more luck with CUDA

UPDATE 3:

First round of GPU memory optimizations. Basically, making all memory allocations a power of two, and packing the data in more efficient datatypes.

So instead of a int32[100] for each board, now I'm using a bool[128], which is equivalent to similarly a char[16] or int32[4]

So I'm getting an 8x speedup from running on the cpu :D

UPDATE 4: 

Jackpot!!

So, tweaking datatypes and the work unit I'm sending to the gpu got me up to a wooping 165x speedup against same algorithm on cpu. I can now find all valid battleship boards in around 6 minutes.

I think I might be able to squeaze a bit more juice out of the gpu still.

UPDATE 5:

It's been a while since the last updates. I've been focusing on the transition from counting the amount of posible boards, to actually generating the matrix with the probabilities for each tile. 

As of last commit, It's taking less than 4 minutes to calculate the probability matrix for an empty board. I call that a success.

So this is the plan moving forward:

Clearly I can't use this method for the first moves of the game, so I can either use some of the other approaches during the first turns, or I can do some caching of the probability matrix for the first turns. At least until the first hit, all games should play out the same. 

UPDATE 6:

This is getting boring. Waiting 4 minutes for each move means there is no way of acheiving my original goal of comparing this algorithm to the other ones. 
If you are reading this and have a multi GPU computer or some money to burn in some AWS GPU instances, feel free to do so. Ping me if you want some help with the code.