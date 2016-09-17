import random
from lib import helpers2
import numpy as np

BOARD_SIZE = helpers2.BOARD_SIZE
SHIP_SIZES = helpers2.SHIP_SIZES

STATE_GAME_OVER = -1
STATE_MISS = 0
STATE_HIT = 1

shipBoards = helpers2.get_ship_positions()

class BattleshipGame():
	def __init__(self):		

		while(True):
			board = np.zeros((BOARD_SIZE,BOARD_SIZE),dtype=np.bool)
			self.base_boards = []
			for x in range(len(SHIP_SIZES)):
				ship = random.choice(shipBoards[x])
				self.base_boards.append(ship)
				board = np.logical_or(board,ship)

			if (np.count_nonzero(sp)==17):
				break
			

		self.board = board
		#print sp.astype(np.int)
		self.remaining_sizes = SHIP_SIZES[:]
		self.hits = np.zeros((BOARD_SIZE,BOARD_SIZE),dtype=np.bool)


	def get_remaining_sizes(self):
		return self.get_remaining_sizes

	def play_turn(self,tile):
		#assert(self.played[x][y]==0)
		#print self.base_boards
		row,column = tile
		if (not self.board[row][column]):
			return  {'code':STATE_MISS,'message':"Miss"}
			

		self.hits[row][column] = True
		for ix, base_board in enumerate(self.base_boards):
			if (not base_board[row,column]):
				continue

			ret = {'code':STATE_HIT,'message':"Hit"}

			if (np.count_nonzero(np.logical_and(self.hits,base_board))==self.remaining_sizes[ix]):
				ret = {'code':STATE_HIT,'message':"Sunk"}
				del self.base_boards[ix]
				del self.remaining_sizes[ix]

				if (np.count_nonzero(np.logical_and(self.hits,self.board))==17):
					ret = {'code':STATE_GAME_OVER,'message':"Game Over"}
			
			return ret

		
		





