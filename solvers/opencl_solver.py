import base_solver as base
import game
from lib import helpers
import numpy as np
import redis
r = redis.StrictRedis(host='localhost', port=6379, db=0)

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
		state = self.get_state(hits,misses)
		target = self.get_from_cache(state)
		if target:
			return self.string_coordinates_to_array(target)

		shipBoards = helpers.get_ship_boards(misses,matrix=True)
		s12 = helpers.shortInterpolate(shipBoards[0],shipBoards[1],9)
		s123 = helpers.shortInterpolate(s12,shipBoards[2],12)
		s45 = helpers.shortInterpolate(shipBoards[3],shipBoards[4],5)
		print "Combinations to Compute: " + str(len(s123)*len(s45))
		target = helpers.opencl_interpolate(helpers.bool2IntArray(s123),helpers.bool2IntArray(s45),hits)

		self.set_to_cache(state,target)
		return self.int_coordinates_to_array(target)

	def get_state(self,hits,misses):
		state = np.copy(hits)
		for miss in misses:
			state[miss[0]][miss[1]] = 2
		print state
		return state

	def get_from_cache(self,state):
		#return None
		key = ""
		for row in state:
			key += "".join(map(str,row))
		#print key
		return r.get(key)

	def set_to_cache(self,state,target):
		key = ""
		for row in state:
			key += "".join(map(str,row))

		r.set(key,target)

	def string_coordinates_to_array(self,coord):
		return [int(coord[0]),int(coord[1])]

	def int_coordinates_to_array(self,coord):
		return [int(coord / 10),int(coord % 10)]



		
		

def play_game(bs_game,solver):
	limit = 100
	misses = []
	hits = np.zeros([10,10],dtype=np.uint8)
	for turn in xrange(limit):
		print misses
		tile = solver.get_next_target(misses,hits)
		print tile
		ret = bs_game.play_turn(tile)
		#solver.mark_tile_used(tile)
		print ret
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
