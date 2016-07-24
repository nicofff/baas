import base_solver as base
import game
from lib import helpers
import numpy as np

STATE_MISS = 0
STATE_HIT = 1
STATE_UNKNOWN = 2
SHIP_SIZES = helpers.SHIP_SIZES


class OpenCLSolver(base.BaseSolver):

	def __init__(self):
		super(OpenCLSolver,self).__init__()
		current_state = np.empty([10,10]).astype(np.uint8)
		current_state.fill(STATE_UNKNOWN);

	def mark_tile_used(self,tile):
		self.remaining_tiles.remove(tile)

	def get_next_target_random(self):
		ret = self.tiles[self.turn]
		self.turn+=1
		return ret

	def get_next_target(self,misses,hits):
		shipBoards = helpers.get_ship_boards(misses,matrix=True)
		s12 = helpers.shortInterpolate(shipBoards[0],shipBoards[1],9)
		s123 = helpers.shortInterpolate(s12,shipBoards[2],12)
		s45 = helpers.shortInterpolate(shipBoards[3],shipBoards[4],5)
		validBoards = helpers.opencl_interpolate(helpers.bool2IntArray(s123),helpers.bool2IntArray(s45),hits)


		
		

def play_game(bs_game,solver):
	limit = 100
	misses = []
	hits = np.zeros([10,10],dtype=np.uint8)
	for turn in xrange(limit):
		
		tile = solver.get_next_target(misses,hits)
		#print tile
		ret = bs_game.play_turn(tile)
		#solver.mark_tile_used(tile)
		#print ret
		if (ret["code"] == STATE_MISS):
			misses.append(tile)
		if (ret["code"] == STATE_HIT):
			x,y = tile
			hits[x][y] = 1

		if (ret["code"] == -1):
			print(turn +1)
			return




solver = OpenCLSolver();

rounds = 1

for x in xrange(rounds):
	bs_game = game.BattleshipGame()
	solver.reset()
	play_game(bs_game,solver)
