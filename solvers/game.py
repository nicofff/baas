import random
from lib import helpers

BOARD_SIZE = helpers.BOARD_SIZE
SHIP_SIZES = helpers.SHIP_SIZES

STATE_GAME_OVER = -1
STATE_MISS = 0
STATE_HIT = 1

shipBoards = helpers.get_ship_boards()

class BattleshipGame():
	def __init__(self):		

		while(True):
			s0 = random.choice(shipBoards[0])[:]
			s1 = random.choice(shipBoards[1])[:]
			s2 = random.choice(shipBoards[2])[:]
			s3 = random.choice(shipBoards[3])[:]
			s4 = random.choice(shipBoards[4])[:]
			b = sorted(s0+s1+s2+s3+s4)


			for ix in range(len(b)-1):
				if b[ix] == b[ix+1]:
					break
			else:
				self.board = b
				self.remaining_sizes = SHIP_SIZES[:]
				self.base_boards = [s0,s1,s2,s3,s4]
				break

	def get_remaining_sizes(self):
		return self.get_remaining_sizes

	def play_turn(self,tile):
		#assert(self.played[x][y]==0)
		#print self.base_boards

		if (tile not in self.board):
			return  {'code':STATE_MISS,'message':"Miss"}
			

		for ix, base_board in enumerate(self.base_boards):
			if (tile not in base_board):
				continue

			ret = {'code':STATE_HIT,'message':"Hit"}
			self.base_boards[ix].remove(tile)

			if (self.base_boards[ix] == []):
				ret = {'code':STATE_HIT,'message':"Sunk"}
				del self.base_boards[ix]
				del self.remaining_sizes[ix]

				if (self.base_boards == []):
					ret = {'code':STATE_GAME_OVER,'message':"Game Over"}
			
			return ret

		
		





