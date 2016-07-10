#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
import numpy as np
import pyopencl as cl

BOARD_SIZE = 10

STATE_MISS = 0
STATE_HIT = 1
STATE_UNKNOWN = 2


shipBoards = []

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

def filterInvalid(current_state,board_array):
	# Assuming we're using the 2board sum logic
	# For the sum of two boards to be valid,
	# all misses in the current state, should also 
	# be misses in both boards
	# The same logic DOES NOT apply to hits
	state_misses = [x for x in range(len(current_state)) if current_state[x]==STATE_MISS]
	valid= []
	for board in board_array:
		board_misses = [x for x in range(len(board)) if board[x]==STATE_MISS]
		mask = np.in1d(state_misses,board_misses)
		if mask.all():
			valid.append(board);

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


def interpolate(bs1,bs2):
	print "Starting computation"

	# This is the plan:
	# We copy our generator boards to opengl memory
	# We generate an index of each posible combination, so index x represent one board from each ship generator boards
	# Then we tell the opengl processor to test a number of ix's to see whether they create a valid board
	ctx = cl.create_some_context()
	prg = cl.Program(ctx, """

	__kernel void sum(__global const char *v1,__global const char *v2, uint v1_index, __global char *res_g) {

	    int work_item = get_global_id(0);
	    int work_size = get_global_size(0);
	    int array_position = get_global_id(1);
	    int array_size = get_global_size(1);


	    res_g[ work_item * array_size + array_position ]=v1[v1_index * array_size + array_position] | v2[ work_item * array_size + array_position];
	}

	__kernel void validate(__global const char *v1, __global char *curr_state,__global char *res_g) {

	    int ix = get_global_id(0);
	    int x,count = 0;
	    uint n,tile, violations = 0;
	    char state;
	    int value;
	    bool hit,miss;
	    for (x=0;x<128;x++){
	    	value = v1[128*ix + x];
    		hit = curr_state[x];
    		count += value;
    		violations += (hit && !tile );    		

	    }


		res_g[ix]= (count==17) && (violations == 0);
	}

	__kernel void matrix_count(__global const char *v1, __global char *valids_g, uint work_size, __global long *out_matrix) {
		int x = get_global_id(0);
		uint i = 0;
		char value;
		long count = 0;
		for (i = 0;i<work_size;i++){
			if(valids_g[i] == 1){
				value = v1[128 * i + x ];

				count += value;
			}
			
		}
		out_matrix[x] += count;



	}
	""").build()
	queue = cl.CommandQueue(ctx)
	mf = cl.mem_flags

	total = 0
	valid = 0

	current_state = np.empty([128]).astype(np.uint8)
	current_state.fill(STATE_MISS);
	#current_state[0] = STATE_MISS;
	#bs1 = filterInvalid(current_state,bs1)
	#bs2 = filterInvalid(current_state,bs2)
	#print len(bs1)
	#print len(bs2)

	s1 = np.array(bs1).astype(np.uint8)
	s2 = np.array(bs2).astype(np.uint8)
	print s2.shape
	s1_g = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=s1)
	s2_g = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=s2)


	current_state_g = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=current_state)



	blockSize = 1

	iterSize= len(bs1)
	iterations = len(bs2) / blockSize

	assert( (len(bs2) / float(blockSize)) %1 == 0 )

	workSize = iterSize * blockSize
	print workSize

	sum_result_np = np.empty([workSize,128]).astype(np.uint8)
	sum_result_np_g = cl.Buffer(ctx, mf.WRITE_ONLY, sum_result_np.nbytes)

	validate_result_np = np.empty([workSize]).astype(np.uint8)
	validate_result_np_g = cl.Buffer(ctx, mf.WRITE_ONLY, validate_result_np.nbytes)

	count_matrix = np.zeros([100]).astype(np.uint64)
	count_matrix_g = cl.Buffer(ctx, mf.COPY_HOST_PTR, hostbuf=count_matrix)

	for step in xrange(iterations):
		print "Tested: " + str(float(step)/(iterations)*100) + "%"

		prg.sum(queue, (workSize,128), None, s2_g, s1_g, np.uint32(step), sum_result_np_g);


##
		#cl.enqueue_copy(queue,sum_result_np, sum_result_np_g).wait()
		# print np.resize(s1[100],(10,10))
		# print np.resize(s2[0],(10,10))
		# print np.resize(sum_result_np[100],(10,10))
		# print 
		# break

# ##
		prg.validate(queue, validate_result_np.shape, None, sum_result_np_g, current_state_g, validate_result_np_g);

		prg.matrix_count(queue, (128,), None, sum_result_np_g, validate_result_np_g, np.uint32(workSize),count_matrix_g);

		# cl.enqueue_copy(queue, validate_result_np, validate_result_np_g)
		# for ix, board in enumerate(validate_result_np):
		# 	if board:
		# 		print np.count_nonzero(sum_result_np[ix])

		# break
		cl.enqueue_copy(queue, count_matrix, count_matrix_g)
		print count_matrix / sum(count_matrix) * 100
		#print sum(count_matrix)


		# print valid
		# print "Valid: " + str(float(valid)/((step+1)*workSize)*100)+"%"

	# print total
	# print "Space searched: " + str(float(total)/combinations *100) + "%"
	# print "Valid boards: " + str(float(valid)/total *100) + "%"
	# print "Valid boards: " + str(valid)
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


#print np.array(shipBoards[0][0]).astype(np.int32)
print "generating s123"
s12 = shortInterpolate(shipBoards[0],shipBoards[1],9)
s123 = shortInterpolate(s12,shipBoards[2],12)
print len(s123)
print "generating s45"
s45 = shortInterpolate(shipBoards[3],shipBoards[4],5)
print len(s45)
validBoards = interpolate(s123,s45)
