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
			#print "loop"
			shipPositions = []
			board = np.zeros((BOARD_SIZE,BOARD_SIZE),dtype=np.int)
			for x in range(len(SHIP_SIZES)):
				ship = random.choice(shipBoards[x])
				shipPositions.append(ship)
				board += ship * (x+1)

			if (np.count_nonzero(board)==17):
				break
			
		self.board=board
		self.shipPositions= shipPositions

		self.notHits = np.ones((BOARD_SIZE,BOARD_SIZE),dtype=np.bool)


	def get_remaining_sizes(self):
		return self.get_remaining_sizes

	def play_turn(self,tile):
		#assert(self.played[x][y]==0)
		#print self.base_boards
		row,column = tile
		value = self.board[row][column]
		if (not value):
			return  {'code':STATE_MISS,'message':"Miss"}
			

		self.notHits[row][column] = False

		ret = {'code':STATE_HIT,'message':"Hit"}
		shipHit = self.shipPositions[value-1]
		if (np.count_nonzero(shipHit * self.notHits)==0):
			ret = {'code':STATE_HIT,'message':"Sunk"}

		if (np.count_nonzero(self.notHits)==83):
			ret = {'code':STATE_GAME_OVER,'message':"Game Over"}

		return ret


