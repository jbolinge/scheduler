#!/usr/bin/env python

import sys
import scheduler as sc
import multiprocessing

def run_scheduler(filename):
	global counter
	savename = filename[:-4] + str(counter) + '.csv'
	sc.run_schedule(filename, savename)

def use_mp(filename, runs):
	global counter
	counter = 0
	jobs = []
	for i in range(runs):
		p = multiprocessing.Process(target=run_scheduler, args=(filename,))
		jobs.append(p)
		p.start()
		counter += 1
	for j in jobs:
		j.join()

if __name__ == '__main__':
	try:
		runs = int(sys.argv[1])
		filename = sys.argv[2]
	except:
		print'Please supply the number of runs (1-8) followed by the input file name'
		sys.exit()
	if (runs < 1 or runs > 8):
		print'Please enter a valid number of runs (1-8)'
		sys.exit()
	print 'Beginning %d runs, check logs for progress.' % runs
	use_mp(filename, runs)
	print '%d runs completed.' % runs