import pyopencl as cl
import numpy as np
np.set_printoptions(linewidth=128)

BOARD_SIZE = 10
SHIP_SIZES = [5,4,3,3,2]


STATE_MISS = 0
STATE_HIT = 1
STATE_UNKNOWN = 2

def bool2IntArray(boolArray):
	ret = []
	for array in boolArray:
		ret.append(np.packbits(array))

	return ret

def int2BoolArray(boolArray):
	ret = []
	for array in boolArray:
		ret.append(np.unpackbits(array))

	return ret


def posible_positions_for_ship(size,exclude_tiles,matrix=False):
	positions = []
	#print exclude_tiles
	for x in range(BOARD_SIZE-size+1):
		positionV = []
		positionH = []
		for j in range(BOARD_SIZE):
			excludeH = False
			excludeV = False
			posH = []
			posV = []
			for i in range(x,x+size):
				if [i,j] in exclude_tiles:
					excludeV = True
				posH.append([i,j])

				if [j,i] in exclude_tiles:
					excludeH = True
				posV.append([j,i])
				
			if (matrix):
				posV = coordinatesToArray(posV)
				posH = coordinatesToArray(posH)
			
			if(not excludeV):
				positionV.append(posV)
			
			if(not excludeH):
				positionH.append(posH)
			

		positions += positionV
		positions += positionH

	return positions


def coordinatesToArray(position):
	array = np.zeros([BOARD_SIZE,BOARD_SIZE],dtype=np.bool)
	for tile in position:
		array[tile[0]][tile[1]] = True
	array = array.flatten()
	array.resize((128,))
	return array

def get_ship_boards(exclude_tiles=[],matrix = False):
	shipBoards = []
	for shipSize in SHIP_SIZES:
		posible = posible_positions_for_ship(shipSize,exclude_tiles,matrix)
		shipBoards.append(posible)

	return shipBoards


def shortInterpolate(ss1,ss2,size):
	validBoards = []
	for s1 in ss1:
		for s2 in ss2:
			b = np.logical_or(s1,s2);
			if(np.count_nonzero(b)==size):
				validBoards.append(b)

	return validBoards



def opencl_interpolate(bs1,bs2,hits):
	print "Starting computation"

	# This is the plan:
	# We copy our generator boards to opengl memory
	# We generate an index of each posible combination, so index x represent one board from each ship generator boards
	# Then we tell the opengl processor to test a number of ix's to see whether they create a valid board
	ctx = cl.create_some_context()
	prg = cl.Program(ctx, """

	__kernel void sum(__global const int *v1,__global const int *v2, __global const int *current_state, uint v1_index, __global int *sum_g ,__global int *valids_g) {

	    int work_item = get_global_id(0);
	    int array_position = work_item  & 3; // % 4

	    int v1_local =v1[v1_index * 4 + array_position];
	    int v2_local =v2[ work_item ];
	    int current_state_local = current_state[array_position];

	    int result = v1_local | v2_local;
	    int overlapping = v1_local & v2_local;
	    int non_matching_hits = (( current_state_local | result) ^ result);

	    valids_g[work_item] = ~(overlapping | non_matching_hits);

	    sum_g[ work_item] = result;
	    
	    
	}

	__kernel void join_validity(__global long *valids) {

	    int ix = get_global_id(0);
	    long v1 = valids[2*ix];
	    long v2 = valids[2*ix + 1];
	    long invalid = (~v1 | ~v2);
	    if (invalid != 0){
	    	valids[2*ix] = 0;
	    	valids[2*ix +1] = 0;
	    }


	}


	__kernel void matrix_count(__global const char *v1, __global char *valids_g, uint work_size, __global long *out_matrix) {
		/*int sector = get_global_id(0);
		int workers = get_global_size(0);
		int board_sector = get_global_id(1);*/
		int ix = get_global_id(0);
		int workers = get_global_size(0) >> 4;
		int sector = ix >> 4;
		int board_sector = ix & 15;
		char local_sector;
		char local_valid;
		uint board;
		long sum[8] = {0};

		uint work_unit = (work_size >> 9) +1 ; // 512 = 2^9

		for (uint board_ix = 0;board_ix < work_unit	; board_ix++){
			board = work_unit * sector + board_ix;
			if (board >= work_size){
				break;
			}
			local_sector = v1[16*board + board_sector];
			local_valid = valids_g[16*board + board_sector];
			for (char tile = 0; tile < 8; tile++){
				sum[tile] += ((local_sector & (1 << 7 - tile)) && local_valid);
				
			}
		}

		for (char position = 0; position < 8; position++){
			out_matrix[sector* 128 + 8*board_sector + position ] += sum[position];
		}


	}


	""").build()
	queue = cl.CommandQueue(ctx)
	mf = cl.mem_flags

	total = 0
	valid = 0

	current_state = np.copy(hits)
	current_state.resize((128,))
	current_state = np.packbits(current_state.astype(np.bool)).astype(np.uint8)

	s1 = np.array(bs1).astype(np.uint8)
	s2 = np.array(bs2).astype(np.uint8)
	s1_g = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=s1)
	s2_g = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=s2)


	current_state_g = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=current_state)




	workSize= len(bs1)
	iterations = len(bs2) 

	sum_result_np = np.empty([workSize,16]).astype(np.uint8)
	sum_result_np_g = cl.Buffer(ctx, mf.WRITE_ONLY, sum_result_np.nbytes)

	valid_np = np.empty([workSize,16]).astype(np.uint8)
	valid_np_g = cl.Buffer(ctx, mf.READ_WRITE, valid_np.nbytes)

	count_matrix = np.zeros([512,128]).astype(np.uint64)
	count_matrix_g = cl.Buffer(ctx, mf.READ_WRITE | mf.COPY_HOST_PTR, hostbuf=count_matrix)
	print_limit=1
	for step in xrange(iterations):
	#for step in xrange(1000):
		tested = float(step)/(iterations)*100
		if tested > print_limit:
			print "Tested: " + str(tested) + "%"
			print_limit+=1

		prg.sum(queue, (workSize * 4,), None, s2_g, s1_g, current_state_g, np.uint32(step), sum_result_np_g, valid_np_g);
		prg.join_validity(queue, (workSize,), None, valid_np_g);
		prg.matrix_count(queue, (512 * 16,), None, sum_result_np_g, valid_np_g, np.uint32(workSize),count_matrix_g);

	cl.enqueue_copy(queue, count_matrix, count_matrix_g)
	total_matrix = sum(count_matrix)
	print np.resize(total_matrix,(10,10))
	print ""
	print np.resize(np.ma.masked_array(total_matrix,mask=np.resize(hits,(128,)),fill_value=0).filled(),(10,10))
	return np.argmax(np.ma.masked_array(total_matrix,mask=np.resize(hits,(128,)),fill_value=0).filled())
