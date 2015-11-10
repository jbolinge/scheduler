#!/usr/bin/env python

#Schedule is Call, Long, Short, MVSC, Vacation, Regina
#1:'Jason', 2:'Brian', 3:'Dick', 4:'Mark', 5:'Tim', 6:'Ryan'

import numpy as np
import itertools
import random
import sys
import math
import logging

def gen_permutations(n, mvsc_list, regina_list):	#Generate all possible combinations for a week's schedule
	p = itertools.permutations(list(range(1,n+1)))
	temp = np.array([list(w) for w in p if w[3] in mvsc_list])
	temp2 = np.array([list(w) for w in temp if w[-1] in regina_list])
	return temp2

def cost(schedule_cand):
	tot_cost = 0
	for i in range(1, len(schedule_cand)):
		if (np.all(schedule_cand[i])):
			if (schedule_cand[i][3] == schedule_cand[i-1][3]):   #Cost to be at MVSC consecutive weeks
				tot_cost += 5
			if (schedule_cand[i][1] == schedule_cand[i-1][1]):   #Cost to be long consecutive weeks
				tot_cost += 2
			if (schedule_cand[i-1][0] == schedule_cand[i][0]):  #cost of back to back call
				tot_cost += 2000
			if (i > 1 and schedule_cand[i][0] == schedule_cand[i-2][0]):	#Cost to be on call 2 times in 3 weeks
				tot_cost += 1000
			if (i > 2 and schedule_cand[i][0] == schedule_cand[i-3][0]):	#Cost to be on call 2 times in 4 weeks
				tot_cost += 50
			if (i > 3 and schedule_cand[i][0] == schedule_cand[i-4][0]):	#Cost to be on call 2 times in 5 weeks
				tot_cost += 10
			if (schedule_cand[i][0] == schedule_cand[i-1][5]):	#Cost to be call following Regina
				tot_cost += 2
			if (schedule_cand[i][4] == schedule_cand[i-1][0]):	 #Cost reduction to be on call prior to vacation
				tot_cost -= 5
			tot_cost += len([q for q in range(6) if schedule_cand[i-1][q] == schedule_cand[i][q]]) #increase cost of being consecutive weeks anywhere
	sum_shifts = np.zeros((4,6))
	for i in range(1,7):
		sum_shifts[0,i-1] = (schedule_cand[1:,0]==i).sum()
		sum_shifts[1,i-1] = (schedule_cand[1:,2]==i).sum()
		sum_shifts[2,i-1] = (schedule_cand[1:,3]==i).sum()
		sum_shifts[3,i-1] = (schedule_cand[1:,5]==i).sum()
	for i in range(4):
		b = np.unique(sum_shifts[i,:])
		if (i == 0 and b[-1] - b[0] > 1):  #equal call (within 1)
			#print 'failed for equal call'
			tot_cost += (2000 * (b[-1] - b[0]))
		if (i == 1 and b[-1] - b[0] > 1):  #equal early (within 1)
			#print 'failed for equal early'
			tot_cost += (50 * (b[-1] - b[0]))
		if (i == 2 and b[-1] - b[1] > 1):  #equal MVSC (within 1)
			#print 'failed for equal mvsc'
			tot_cost += (50 * (b[-1] - b[1]))
		if (i == 3 and b[-1] - b[1] > 12):  #equal Regina (within 12)
			#print 'failed for equal regina'
			diff = (b[-1] - b[1]) - 12
			if diff < 0:
				diff = 0
			tot_cost += (50 * diff)
	return tot_cost

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
	global master_cand
	master_cand = schedule_cand.copy()
	init_temp = 1000
	temperature = init_temp
	base_temp = 0.01
	cooling_factor = 0.99
	iters_per_temp = 100
	reheating_frequency = 0.002
	reheating_factor = 10
	reset_frequency = 0.0002
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
					print 'new overall best: %d\tTemperature = %.2f' % (overall_best_cost, temperature)
					#print best_schedule
			else:
				schedule_cand[week] = temp
		temperature *= cooling_factor
		if random.random() < reheating_frequency:
			temperature *= reheating_factor
			if temperature > init_temp:
				temperature = init_temp
		if random.random() < reset_frequency:
			schedule_cand = best_schedule.copy()
			current_cost = overall_best_cost
			#print 'Reset to best_schedule.  Temperature = %.2f\tCost = %d' % (temperature, overall_best_cost)
	print best_schedule
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
	print schedule_cand
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
