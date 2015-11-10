#!/usr/bin/env python

import sys
import scheduler as sc
import sim_anneal as sa
import multiprocessing
import json

def run_scheduler(filename, counter):
	savename = conf['output_file'] + str(counter) + '.csv'
	if conf['use_sa']:
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
	global conf
	with open('config.json', 'r') as f:
		conf = json.load(f)
	print 'Beginning %d runs, check logs for progress.' % conf['num_cores']
	use_mp(conf['input_file'], conf['num_cores'])
	print '%d runs completed.' % conf['num_cores']
