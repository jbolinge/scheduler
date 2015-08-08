#!/usr/bin/env python

import sys
import scheduler as sc
import sim_anneal as sa
import multiprocessing

def run_scheduler(filename, counter):
	savename = filename[:-4] + str(counter) + '.csv'
	if use_sa:
		sa.run_schedule(filename, savename)
	else:
		sc.run_schedule(filename, savename)

def use_mp(filename, runs):
	counter = 0
	jobs = []
	for i in range(runs):
		p = multiprocessing.Process(target=run_scheduler, args=(filename, counter))
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
	global use_sa
	use_sa = True
	use_mp(filename, runs, use_sa)
	print '%d runs completed.' % runs
