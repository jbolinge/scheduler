#!/usr/bin/env python

#Schedule is Call, Long, Short, MVSC, Vacation, Regina
#1:'Jason', 2:'Brian', 3:'Dick', 4:'Mark', 5:'Tim', 6:'Ryan'

import numpy as np
import itertools
import random
import sys
import math
import logging
import two_opt
from cost import cost

def gen_permutations(n, mvsc_list, regina_list):	#Generate all possible combinations for a week's schedule
	p = itertools.permutations(list(range(1,n+1)))
	temp = np.array([list(w) for w in p if w[3] in mvsc_list])
	temp2 = np.array([list(w) for w in temp if w[-1] in regina_list])
	return temp2

def get_cands(week):
	cands = list()
	filled = list(itertools.chain.from_iterable(np.nonzero(master_cand[week])))
	for perm in perm_list:
		truth_array = (master_cand[week]==perm)
		if (np.array([truth_array[f] for f in filled]).all()):
			if (master_cand[week-1][4] != perm[0]):	#No call following vacation
				cands.append(perm)
	rand_index = random.randint(0, len(cands) - 1)
	return cands[rand_index]

def accept(new_cost, old_cost, temperature):
	if new_cost < old_cost:
		return 1.0
	result = math.exp((old_cost - new_cost) / temperature)
	return result

def rand_fill(schedule_cand):
	for i in range(1,53):
		schedule_cand[i,:] = get_cands(i)
	return schedule_cand

def gen_schedules(schedule_cand):		#Generate schedule candidates using simulated annealing
	global master_cand, final
	master_cand = schedule_cand.copy()
	final = False
	init_temp = 1000
	temperature = init_temp
	base_temp = 0.01
	cooling_factor = 0.99
	iters_per_temp = 100
	reheating_frequency = 0.002
	reheating_factor = 10
	reset_frequency = 0.0003
	two_opt_freq = 0.01
	overall_best_cost = 99999999
	schedule_cand = rand_fill(schedule_cand)
	best_schedule = schedule_cand.copy()
	current_cost = cost(schedule_cand)
	while temperature > base_temp:
		for q in range(iters_per_temp):
			week = random.randint(1,52)
			temp = np.array(schedule_cand[week])
			schedule_cand[week] = get_cands(week)
			new_cost = cost(schedule_cand)
			if (accept(new_cost, current_cost, temperature) > random.random()):
				current_cost = new_cost
				#print 'Current cost: %d\tTemp: %.3f' % (current_cost, temperature)
				if current_cost < overall_best_cost:
					overall_best_cost = current_cost
					best_schedule = schedule_cand.copy()
					#print 'new overall best: %d\tTemperature = %.2f' % (overall_best_cost, temperature)
					#print best_schedule
			else:
				schedule_cand[week] = temp
		temperature *= cooling_factor
		if random.random() < reheating_frequency:
			temperature *= reheating_factor
			if temperature > init_temp:
				temperature = init_temp
			#print 'Reheating, Temperature = %.2f\tCost = %d' % (temperature, current_cost)
		if random.random() < reset_frequency:
			schedule_cand = best_schedule.copy()
			current_cost = overall_best_cost
			#print 'Reset to best_schedule.  Temperature = %.2f\tCost = %d' % (temperature, overall_best_cost)
		if random.random() < two_opt_freq:
			schedule_cand = two_opt.gen_schedules(schedule_cand, 'schedule_2015.csv')
			current_cost = cost(schedule_cand)
			if current_cost < overall_best_cost:
					overall_best_cost = current_cost
					best_schedule = schedule_cand.copy()
					#print 'new overall best: %d\tTemperature = %.2f\tTwo_opted' % (overall_best_cost, temperature)
	#print best_schedule
	#print 'Totals:'
	#for i in range(1,7):
		#print 'Person %d' % i
		#print sum(best_schedule[:,:]==i)
	#final = True
	#cost(best_schedule)
	best_schedule = two_opt.gen_schedules(best_schedule, 'schedule_2015.csv')
	return best_schedule

def read_input(filename):
	schedule_cand = np.genfromtxt(filename, delimiter=',')
	assert schedule_cand.shape==(53,6)
	return schedule_cand

def save_result(filename, schedule_cand):
	np.savetxt('schedules/' + filename, schedule_cand, delimiter=',')
	logging.info('saved schedule to schedules/%s', filename)

def run_schedule(s_filename, savename):
	global perm_list
	logging.basicConfig(filename='log/' + savename + '.log', format='%(asctime)s %(message)s', \
		datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO, mode='w')
	regina_list = [1, 2, 5, 6]
	mvsc_list = [1, 2, 3, 6]
	perm_list = gen_permutations(6, mvsc_list, regina_list)
	schedule_cand = read_input(s_filename)
	#print schedule_cand
	logging.info('beginning schedule generation using simulated annealing')
	schedule_cand = gen_schedules(schedule_cand)
	logging.info('finished schedule generation, best cost %d', cost(schedule_cand))
	save_result(savename, schedule_cand)

if __name__ == "__main__":
	try:
		s_filename = sys.argv[1]
		savename = sys.argv[2]
	except:
		print'Please supply the name of the input file and output file'
		sys.exit()
	run_schedule(s_filename, savename)
