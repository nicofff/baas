import base_solver as base
import game
from lib import helpers


STATE_MISS = 0
STATE_HIT = 1
STATE_UNKNOWN = 2

SEARCH_MODE = 0
DESTROY_MODE = 1

DESTROY_LEFT = 0
DESTROY_RIGHT = 1
DESTROY_UP = 2
DESTROY_DOWN = 3

class SmartSolver(base.BaseSolver):

	def mark_tile_used(self,tile):
		self.remaining_tiles.remove(tile)

	def get_random_target(self):
		ret = self.tiles[self.turn]
		self.turn+=1
		return ret
		
		

def play_game(bs_game,solver):
	limit = 100
	mode = SEARCH_MODE
	for turn in xrange(limit):
		tile = solver.get_random_target()
		#print tile
		ret = bs_game.play_turn(tile)
		if (ret = STATE_HIT && mode = SEARCH_MODE:
			mode = DESTROY_MODE
			originalHit = tile
			destroy = DESTROY_LEFT





		#solver.mark_tile_used(tile)
		#print ret
		if (ret["code"] == -1):
			print(turn +1)
			return



solver = RandomSolver();

rounds = 100000

for x in xrange(rounds):
	bs_game = game.BattleshipGame()
	solver.reset()
	play_game(bs_game,solver)
