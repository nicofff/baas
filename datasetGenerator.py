import numpy as np

BOARD_SIZE = 10

shipBoards = []




def coordinatesToArray(position):
	array = np.zeros([BOARD_SIZE,BOARD_SIZE],dtype=int)
	for tile in position:
		array[tile[0]][tile[1]] = 1
	return array

def posiblePositionsForShip(size):
	positions = []
	for x in range(BOARD_SIZE-size+1):
		positionV = [coordinatesToArray([(i,j) for i in range(x,x+size)]) for j in range(BOARD_SIZE)]
		positionH = [coordinatesToArray([(j,i) for i in range(x,x+size)]) for j in range(BOARD_SIZE)]
		positions += positionV
		positions += positionH

	return positions


def interpolate(shipboards):
	validBoards = []
	combinations = 120*140*160*160*180
	total = 0
	valid = 0
	for s1 in shipboards[0]:
		for s2 in shipboards[1]:
			board1 = s1 + s2
			if np.count_nonzero(board1) != 9:
				total += 160 *160*180
				continue

			for s3 in shipboards[2]:
				board2 = board1 + s3
				if np.count_nonzero(board2) != 12:
					total += 160*180
					continue

				for s4 in shipboards[3]:
					board3 = board2 + s4
					if np.count_nonzero(board3) != 15:
						total += 180
						continue

					for s5 in shipboards[4]:
						total +=1
						board4 = board3 + s5

						if np.count_nonzero(board4) == 17:
							#print "valid"
							valid+=1

			print "Space searched: " + str(float(total)/combinations *100) + "%"
			print "Valid boards: " + str(float(valid)/total *100) + "%"
			print "Valid boards: " + str(valid)
	return valid



for shipSize in [5,4,3,3,2]:
	posible = posiblePositionsForShip(shipSize)
	#print len(posible)
	shipBoards.append(posible)


validBoards = interpolate(shipBoards)


for board in reversed(validBoards):
	print board
	raw_input("Press Enter to continue...")