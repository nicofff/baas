#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
import numpy as np
import pyopencl as cl

BOARD_SIZE = 10

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


def ix_to_coord(ix):
	z = ix % 180
	res = ix / 180
	y = res % 160
	res = res / 160
	x = res % 160
	res = res / 160
	w = res % 140
	res = res / 140
	v = res 
	return (v,w,x,y,z)

def interpolate(bs1,bs2):
	print "Starting computation"

	# This is the plan:
	# We copy our generator boards to opengl memory
	# We generate an index of each posible combination, so index x represent one board from each ship generator boards
	# Then we tell the opengl processor to test a number of ix's to see whether they create a valid board
	ctx = cl.create_some_context()
	prg = cl.Program(ctx, """

	__kernel void sum(__global const char *v1,__global const char *v2, __global int *v1_ix, __global char *res_g) {

	    int x = get_global_id(0);
	    int y = get_global_id(1);
	    int v1_index = v1_ix[0];
	    res_g[ 16 * x + y ]=v1[16*v1_index + y] | v2[16 * x + y];
	}

	__kernel void validate(__global const char *v1, __global int *res_g) {

	    int ix = get_global_id(0);
	    int x,count = 0;
	    for (x=0;x<16;x++){
	    	int value = v1[16*ix + x];
	    	count+= (value & 1) != 0;
	    	count+= (value & 2) != 0;
	    	count+= (value & 4) != 0;
	    	count+= (value & 8) != 0;
	    	count+= (value & 16) != 0;
	    	count+= (value & 32) != 0;
	    	count+= (value & 64) != 0;
	    	count+= (value & 128) != 0;

	    }
		res_g[ix]= (count==17);
	}

	""").build()
	queue = cl.CommandQueue(ctx)
	mf = cl.mem_flags

	combinations = 120*140*160*160*180
	total = 0
	valid = 0

	s1 = np.array(bs1).astype(np.uint8)
	s2 = np.array(bs2).astype(np.uint8)
	s1_g = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=s1)
	s2_g = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=s2)
	

	iterSize= len(bs2)
	iterations = len(bs1)

	sum_result_np = np.empty([iterSize,16]).astype(np.uint8)
	sum_result_np_g = cl.Buffer(ctx, mf.WRITE_ONLY, sum_result_np.nbytes)

	validate_result_np = np.empty([iterSize]).astype(np.int32)	
	validate_result_np_g = cl.Buffer(ctx, mf.WRITE_ONLY, validate_result_np.nbytes)

	for step in xrange(iterations):
		print str(float(step)/(iterations)*100) + "%"

		ixs = np.array([step]).astype(np.int32)
		s1_ix = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=ixs)

		prg.sum(queue, (iterSize,16), None, s1_g, s2_g, s1_ix,sum_result_np_g);


###
		# cl.enqueue_copy(queue, sum_result_np, sum_result_np_g).wait()
		# print np.resize(int2BoolArray(s1)[0],(10,10))
		# print np.resize(int2BoolArray(s2)[128],(10,10))
		# print np.resize(int2BoolArray(sum_result_np)[128],(10,10))
		# print 
		# break

###
		prg.validate(queue, validate_result_np.shape, None, sum_result_np_g, validate_result_np_g);

		cl.enqueue_copy(queue, validate_result_np, validate_result_np_g).wait()

		valid += np.count_nonzero(validate_result_np)
		print valid
		print str(float(valid)/(step*iterSize+1)*100)+"%"

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
