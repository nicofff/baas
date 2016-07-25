#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import
import numpy as np
import pyopencl as cl

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


	__kernel void matrix_count(__global const int *v1, __global int *valids_g, uint work_size, __global long *out_matrix) {
		int sector = get_global_id(0);
		int workers = get_global_size(0);
		int board_sector = get_global_id(1);
		int local_sector;
		int local_valid;
		uint offset,board;
		char bit_ix;
		long sum[32] = {0};
		char bit, byte;

		uint work_unit = work_size / workers +1 ;

		for (uint board_ix = 0;board_ix < work_unit	; board_ix++){
			board = work_unit * sector + board_ix;
			if (board >= work_size){
				break;
			}
			local_sector = v1[4*board + board_sector];
			local_valid = valids_g[4*board + board_sector];
			for (char tile = 0; tile < 32; tile++){
				bit = tile & 7;
				byte = (tile & 24) >> 3;

				bit_ix = 8*byte - bit + 7;

				sum[tile] += (((local_sector & (1 << bit_ix))) && local_valid);
				
			}
		}

		for (char position = 0; position < 32; position++){
			out_matrix[sector* 128 + 32*board_sector + position ] += sum[position];
		}


	}


	""").build()
	queue = cl.CommandQueue(ctx)
	mf = cl.mem_flags

	total = 0
	valid = 0

	current_state = np.empty([128]).astype(np.bool)
	current_state.fill(False);
	current_state[0] = STATE_HIT;
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



	blockSize = 1

	iterSize= len(bs1)
	iterations = len(bs2) / blockSize

	assert( (len(bs2) / float(blockSize)) %1 == 0 )

	workSize = iterSize * blockSize
	print workSize

	sum_result_np = np.empty([workSize,16]).astype(np.uint8)
	sum_result_np_g = cl.Buffer(ctx, mf.WRITE_ONLY, sum_result_np.nbytes)

	valid_np = np.empty([workSize,16]).astype(np.uint8)
	valid_np_g = cl.Buffer(ctx, mf.READ_WRITE, valid_np.nbytes)

	count_matrix = np.zeros([512,128]).astype(np.uint64)
	count_matrix_g = cl.Buffer(ctx, mf.READ_WRITE | mf.COPY_HOST_PTR, hostbuf=count_matrix)

	#for step in xrange(iterations):
	for step in xrange(1000):
		print "Tested: " + str(float(step)/(iterations)*100) + "%"

		prg.sum(queue, (workSize * 4,), None, s2_g, s1_g, current_state_g, np.uint32(step), sum_result_np_g, valid_np_g);
		prg.join_validity(queue, (workSize,), None, valid_np_g);
		# cl.enqueue_copy(queue, valid_np, valid_np_g)
		# ix = 0
		# for board in valid_np:
		# 	if board[0]!=0:
		# 		print ix
		# 	ix+=1
		# break

		prg.matrix_count(queue, (512,4), None, sum_result_np_g, valid_np_g, np.uint32(workSize),count_matrix_g);

	cl.enqueue_copy(queue, count_matrix, count_matrix_g)
	total_matrix = np.resize(sum(count_matrix),(10,10))
	print total_matrix
	print total_matrix.astype(np.float) / sum(sum(total_matrix))
		#break

	#cl.enqueue_copy(queue, count_matrix, count_matrix_g)
	#print np.resize(sum(count_matrix),(10,10))

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
