#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import
import numpy as np
import pyopencl as cl
import random
np.set_printoptions(linewidth=120)
BOARD_SIZE = 10

STATE_MISS = 0
STATE_HIT = 1
STATE_UNKNOWN = 2

np.set_printoptions(linewidth=128)
shipBoards = []

def bool2IntArray(boolArray):
	ret = []
	for array in boolArray:
		ret.append(np.packbits(array))

	return ret

def int2BoolArray(boolArray):
	ret = []
	for array in boolArray:
		ret.append(np.unpackbits(array).astype(np.uint64))
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
	/** 
	* Return the position of the ships from both boards if there is not overlap between them, and the current state hits match ship positions
	* Returns all zeros otherwise
	**/ 

	__kernel void sum(__global const long2 *v1,__global const long2 *v2, __global const long2 *current_state, uint v1_index, __global long2 *sum_g,__global char *flag_g) {

	    int work_item = get_global_id(0);
	    int array_position = work_item;

	    long2 v1_local =v1[v1_index];
	    long2 v2_local =v2[ work_item ];
	    long2 current_state_local = current_state[0];
		long2 result;
		long2 overlapping;
		long2 non_matching_hits;
		long2 invalid_local;
		long2 sum;
		char flag = 1;
		// For x
	    result.x = v1_local.x | v2_local.x;
	    overlapping.x = v1_local.x & v2_local.x;
	    non_matching_hits.x = (( current_state_local.x | result.x) ^ result.x);

	    invalid_local.x = (overlapping.x | non_matching_hits.x);

	    // For y

	    result.y = v1_local.y | v2_local.y;
	    overlapping.y = v1_local.y & v2_local.y;
	    non_matching_hits.y = (( current_state_local.y | result.y) ^ result.y);
	    invalid_local.y = (overlapping.y | non_matching_hits.y);

	    long invalid = ((invalid_local.x) | (invalid_local.y));

	    if (invalid != 0){
	    	result.x = 0;
	    	result.y = 0;
	    	flag = 0;

	    }

	    sum_g[ work_item] = result;
	    flag_g[work_item] = flag;
	    
	    
	    
	}


	__kernel void matrix_count(__global const char *v1, uint work_size, __global long8 *out_matrix) {

		union {
			long sum[8];
			long8 out_vector;
		} element;

		int offset = get_global_size(0);
		int ix = get_global_id(0);
		element.out_vector = out_matrix[ix];

		char section;
		do{
			section = v1[ix];
			for (char i=0;i<8;i++){
				element.sum[7-i]+= (section & (1 << i))!=0;
			}
			ix+=offset;
		} while (ix  < work_size*16);

		ix = get_global_id(0);
		out_matrix[ix] = element.out_vector;

	}


	""").build()
	queue = cl.CommandQueue(ctx)
	mf = cl.mem_flags
	print(mf)
	total = 0
	valid = 0

	current_state = np.empty([128]).astype(np.bool)
	current_state.fill(False);
	# current_state[22] = STATE_HIT;
	# current_state[87] = STATE_HIT;
	current_state = np.packbits(current_state).astype(np.uint8)
	#bs1 = filterInvalid(current_state,bs1)
	#bs2 = filterInvalid(current_state,bs2)
	#print len(bs1)
	#print len(bs2)

	s1 = np.array(bs1).astype(np.uint8)
	s2 = np.array(bs2).astype(np.uint8)

	s1_g = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=s1)
	s2_g = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=s2)


	current_state_g = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=current_state)



	iterations = len(bs2)
	workSize = len(bs1)
	print workSize

	sum_result_np = np.empty([workSize,16]).astype(np.uint8)
	sum_result_np_g = cl.Buffer(ctx, mf.WRITE_ONLY | mf.HOST_READ_ONLY, sum_result_np.nbytes)

	sum_flag_np = np.empty([workSize,]).astype(np.uint8)
	sum_flag_np_g = cl.Buffer(ctx, mf.WRITE_ONLY | mf.HOST_READ_ONLY, sum_result_np.nbytes)

	count_matrix = np.zeros([1024,128]).astype(np.uint64)
	count_matrix_g = cl.Buffer(ctx, mf.READ_WRITE | mf.COPY_HOST_PTR, hostbuf=count_matrix)
	print_limit = 0.01
	for step in xrange(iterations):
	#for step in xrange(1000):
		print(step)
		tested = float(step)/(iterations)*100
		if tested > print_limit:
			print "Tested: " + str(tested) + "%"
			print_limit+=0.01

		if step == 0:
			prg.sum(queue, (workSize,), None, s2_g, s1_g, current_state_g, np.uint32(step), sum_result_np_g,sum_flag_np_g);
		cl.enqueue_copy(queue, sum_result_np,sum_result_np_g)
		cl.enqueue_copy(queue, sum_flag_np,sum_flag_np_g)
		if step < iterations -1:
			prg.sum(queue, (workSize,), None, s2_g, s1_g, current_state_g, np.uint32(step + 1), sum_result_np_g,sum_flag_np_g);
		out = [sum_result_np[ix] for ix in xrange(len(sum_result_np)) if sum_flag_np[ix]]
		np.save("out/"+str(step)+".npy",out)
	assert(False)
		# ix = random.randint(0,workSize-1)
		# print np.resize(np.unpackbits(bs2[step]),(10,10))
		# print np.resize(np.unpackbits(bs1[ix]),(10,10))
		# this = np.resize(sum(int2BoolArray(sum_result_np)),(10,10))
		# print this
		#prg.matrix_count(queue, (16*1024,), None, sum_result_np_g, np.uint32(workSize),count_matrix_g);
		#break

	assert(False)
	cl.enqueue_copy(queue, count_matrix, count_matrix_g)
	#print  np.resize(count_matrix[511],(10,10))
	total_matrix = np.resize(sum(count_matrix),(10,10))
	# print that -this
	# total_matrix = sum(count_matrix)
	print total_matrix
	print total_matrix.astype(np.float) / sum(sum(total_matrix))
		#break

	# cl.enqueue_copy(queue, count_matrix, count_matrix_g)
	# print np.resize(sum(count_matrix),(10,10))

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
validBoards = interpolate(bool2IntArray(s123),bool2IntArray(s45))
