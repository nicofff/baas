#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
import numpy as np
import pyopencl as cl

BOARD_SIZE = 10

shipBoards = []

def coordinatesToArray(position):
	array = np.zeros([BOARD_SIZE,BOARD_SIZE],dtype=np.uint32)
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
	ctx = cl.create_some_context()
	prg = cl.Program(ctx, """
	__kernel void sum(__global const int *source,  __global int *res_g) {
		int i = get_global_id(1); 
	    int j = get_global_id(0);
	    res_g[i * 10 + j] = 0;
	    for (int x=0;x<5;x++){
	    	res_g[i * 10 + j] += source[x*100 + i * 10 + j];
	    }
		
	}
	""").build()
	queue = cl.CommandQueue(ctx)
	mf = cl.mem_flags

	combinations = 120*140*160*160*180
	total = 0
	valid = 0
	for s1 in shipboards[0]:
		for s2 in shipboards[1]:
			for s3 in shipboards[2]:
				for s4 in shipboards[3]:
					for s5 in shipboards[4]:
						total +=1
						source = np.array([s1,s2,s3,s4,s5])
						source_g = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=source)
						res_g = cl.Buffer(ctx, mf.WRITE_ONLY, s1.nbytes)
						prg.sum(queue, shipBoards[0][0].shape, None, source_g, res_g)
						res_np = np.empty_like(shipBoards[0][0])
						cl.enqueue_copy(queue, res_np, res_g)

						if np.count_nonzero(res_np) == 17:
							#print "valid"
							valid+=1

					print total
					print "Space searched: " + str(float(total)/combinations *100) + "%"
					print "Valid boards: " + str(float(valid)/total *100) + "%"
					print "Valid boards: " + str(valid)
	return valid


for shipSize in [5,4,3,3,2]:
	posible = posiblePositionsForShip(shipSize)
	#print len(posible)
	shipBoards.append(posible)





interpolate(shipBoards)



# Check on CPU with Numpy:
print res_np
print shipBoards[0][0]+shipBoards[1][10]+shipBoards[2][18]+shipBoards[3][47]+shipBoards[4][92]



