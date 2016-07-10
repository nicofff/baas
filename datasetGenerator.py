import numpy as np


BOARD_SIZE = 10

shipBoards = []




def coordinatesToArray(position):
	array = np.zeros([BOARD_SIZE,BOARD_SIZE],dtype=np.bool)
	for tile in position:
		array[tile[0]][tile[1]] = True
	array = array.flatten()
	array.resize((128,))
	return array

def posiblePositionsForShip(size):
	positions = []
	for x in range(BOARD_SIZE-size+1):
		positionV = [coordinatesToArray([(i,j) for i in range(x,x+size)]) for j in range(BOARD_SIZE)]
		positionH = [coordinatesToArray([(j,i) for i in range(x,x+size)]) for j in range(BOARD_SIZE)]
		positions += positionV
		positions += positionH

	return positions


def count_interpolate(ss1,ss2):
	validBoards = []
	combinations = len(ss1)*len(ss2)
	last = 0
	total = 0
	valid = 0
	for s1 in ss2:
		for s2 in ss1:
			total+=1
			board1 = np.logical_or(s1,s2);
			if np.count_nonzero(board1) == 17:
				valid+=1

		print "Space searched: " + str(float(total)/combinations *100) + "%"
		print "Valid boards: " + str(float(valid)/total *100) + "%"
		print "Valid boards: " + str(valid)
		print valid - last
		last = valid
	return valid


def shortInterpolate(ss1,ss2,size):
	validBoards = []
	for s1 in ss1:
		for s2 in ss2:
			b = np.logical_or(s1,s2);
			if(np.count_nonzero(b)==size):
				validBoards.append(b)

	return validBoards


for shipSize in [5,4,3,3,2]:
	posible = posiblePositionsForShip(shipSize)
	#print len(posible)
	shipBoards.append(posible)


#print shipBoards[0][0:5]
s12 = shortInterpolate(shipBoards[0],shipBoards[1],9)
s123 = shortInterpolate(s12,shipBoards[2],12)
print len(s123)
s45 = shortInterpolate(shipBoards[3],shipBoards[4],5)
print len(s45)
validBoards = count_interpolate(s123,s45)


# for board in reversed(validBoards):
# 	print board
# 	raw_input("Press Enter to continue...")