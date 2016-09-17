import numpy as np
np.set_printoptions(linewidth=128)

BOARD_SIZE = 10
SHIP_SIZES = [5,4,3,3,2]


STATE_MISS = 0
STATE_HIT = 1
STATE_UNKNOWN = 2


def posible_positions_for_ship(size):
	# Returns array of Numpy Arrays where each array represents
	# a valid position for that ship
	positions = []
	emptyBoard = np.zeros((BOARD_SIZE,BOARD_SIZE),dtype=bool)
	for offset in range(BOARD_SIZE-size+1):
		# Lets create the basic column with this position offset
		baseColumn = np.zeros(BOARD_SIZE,dtype=np.bool)
		#And fill it from offset to ship size
		for shipTile in range(size):
			baseColumn[offset+shipTile] = True

		#Now place that in every column an rom
		for index in range(BOARD_SIZE):
			position = np.copy(emptyBoard)
			position[index]=baseColumn
			positions.append(position)

			position = np.copy(emptyBoard)
			position[:,index]=baseColumn
			positions.append(position)

	return positions


def get_ship_positions():
	shipBoards = []
	for shipSize in SHIP_SIZES:
		posible = posible_positions_for_ship(shipSize)
		shipBoards.append(posible)

	return shipBoards
