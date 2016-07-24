import pyopencl as cl
import numpy as np

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

	__kernel void sum(__global const int *v1,__global const int *v2, __global int *v1_ix, __global int *res_g) {

	    int x = get_global_id(0);
	    int x_size = get_global_size(0);
	    int y = get_global_id(1);
	    int y_size = get_global_size(1);
	    int z = get_global_id(2);
	    int z_size = get_global_size(2);
	    int v1_index = v1_ix[0]+y;


	    res_g[ y * x_size * z_size + z_size * x + z ]=v1[z_size*v1_index + z] | v2[z_size * x + z];
	}

	__kernel void validate(__global const int *v1, __global char *curr_state,__global char *res_g) {

	    int ix = get_global_id(0);
	    int x,count = 0;
	    uint n,tile, violations = 0;
	    char state;
	    int value;
	    bool hit,miss;
	    for (x=0;x<4;x++){
	    	value = v1[4*ix + x];
	    	for (n=0;n<32;n++){
	    		hit = curr_state[n*x];
	    		tile = ((value & (1 << n)) != 0);
	    		count+= tile;
	    		violations += (hit && !tile );
	    	}

	    }


		res_g[ix]= (count==17) && (violations == 0);
	}

	__kernel void matrix_count(__global const int *v1, __global char *valids_g, uint work_size, __global uint *out_matrix) {
		int x = get_global_id(0);
		uint n, i = 0;
		uint value;
		int count[128] = {0};
		for (i = 0;i<work_size;i++){
			if(valids_g[i]){
				value = v1[4 * work_size + x ];
				for (n=0;n<32;n++){
					out_matrix[4*x + n] += ((value & (1 << n)) != 0);
				}
			}
			
		}


	}
	""").build()
	queue = cl.CommandQueue(ctx)
	mf = cl.mem_flags

	total = 0
	valid = 0

	current_state = hits
	print current_state

	s1 = np.array(bs1).astype(np.uint8)
	s2 = np.array(bs2).astype(np.uint8)
	s1_g = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=s1)
	s2_g = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=s2)


	current_state_g = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=current_state)



	blockSize = 8

	iterSize= len(bs1)
	iterations = len(bs2) / blockSize

	assert( (len(bs2) / float(blockSize)) %1 == 0 )

	workSize = iterSize * blockSize


	sum_result_np = np.empty([workSize,16]).astype(np.uint8)
	sum_result_np_g = cl.Buffer(ctx, mf.WRITE_ONLY, sum_result_np.nbytes)

	validate_result_np = np.empty([workSize]).astype(np.uint8)
	validate_result_np_g = cl.Buffer(ctx, mf.WRITE_ONLY, validate_result_np.nbytes)
	
	count_matrix = np.empty([128]).astype(np.uint32)
	count_matrix_g = cl.Buffer(ctx, mf.WRITE_ONLY| mf.COPY_HOST_PTR, hostbuf=count_matrix)
	for step in xrange(iterations):

		print "Tested: " + str(float(step)/(iterations)*100) + "%"

		ixs = np.array([step*blockSize]).astype(np.int32)
		s1_ix = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=ixs)

		prg.sum(queue, (iterSize,blockSize,4), None, s2_g, s1_g, s1_ix,sum_result_np_g);


##
		# cl.enqueue_copy(queue, sum_result_np, sum_result_np_g).wait()
		# print np.resize(int2BoolArray(s1)[0],(10,10))
		# print np.resize(int2BoolArray(s2)[0],(10,10))
		# print np.resize(int2BoolArray(sum_result_np)[0],(10,10))
		# print 
		# break

##
		prg.validate(queue, validate_result_np.shape, None, sum_result_np_g, current_state_g, validate_result_np_g);
		prg.matrix_count(queue, (4,), None, sum_result_np_g, validate_result_np_g, np.uint32(workSize),count_matrix_g);


		cl.enqueue_copy(queue, count_matrix, count_matrix_g)
		print count_matrix


		print valid
		print "Valid: " + str(float(valid)/((step+1)*workSize)*100)+"%"

	# print total
	# print "Space searched: " + str(float(total)/combinations *100) + "%"
	# print "Valid boards: " + str(float(valid)/total *100) + "%"
	# print "Valid boards: " + str(valid)
	return valid
