import base_solver as base
import game


STATE_MISS = 0
STATE_HIT = 1
STATE_UNKNOWN = 2


class RandomSolver(base.BaseSolver):

	def mark_tile_used(self,tile):
		self.remaining_tiles.remove(tile)

	def get_next_target(self):
		ret = self.tiles[self.turn]
		self.turn+=1
		return ret
		
		

def play_game(bs_game,solver):
	limit = 100
	for turn in xrange(limit):
		tile = solver.get_next_target()
		#print tile
		ret = bs_game.play_turn(tile)
		#solver.mark_tile_used(tile)
		#print ret
		if (ret["code"] == -1):
			#print(turn +1)
			return



solver = RandomSolver();

rounds = 20000

for x in xrange(rounds):
	bs_game = game.BattleshipGame()
	solver.reset()
	play_game(bs_game,solver)
	#print x
