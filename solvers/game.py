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
			s0 = random.choice(shipBoards[0])
			s1 = random.choice(shipBoards[1])

			sp = np.logical_or(s0,s1)
			if (np.count_nonzero(sp)!=9):
				continue

			s2 = random.choice(shipBoards[2])
			sp = np.logical_or(sp,s2)
			if (np.count_nonzero(sp)!=12):
				continue

			s3 = random.choice(shipBoards[3])
			sp = np.logical_or(sp,s3)
			if (np.count_nonzero(sp)!=15):
				continue

			s4 = random.choice(shipBoards[4])
			sp = np.logical_or(sp,s4)
			if (np.count_nonzero(sp)!=17):
				continue
			
			break

		self.board = sp
		#print sp.astype(np.int)
		self.remaining_sizes = SHIP_SIZES[:]
		self.base_boards = [s0,s1,s2,s3,s4]
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

			if (np.array_equal(np.logical_and(self.hits,base_board),base_board)):
				ret = {'code':STATE_HIT,'message':"Sunk"}
				del self.base_boards[ix]
				del self.remaining_sizes[ix]

				if (np.array_equal(np.logical_and(self.hits,self.board),self.board)):
					ret = {'code':STATE_GAME_OVER,'message':"Game Over"}
			
			return ret

		
		





