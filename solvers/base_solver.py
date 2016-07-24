import random

ALL_TILES = [[x,y] for x in range(10) for y in range(10)]
random.shuffle(ALL_TILES)

class BaseSolver(object):
	def __init__ (self):
		self.reset()

	def reset(self):
		self.tiles = ALL_TILES
		self.turn=0

	def get_next_target(self,current_board):
		pass