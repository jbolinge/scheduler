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
		if (schedule_cand[i][3] == schedule_cand[i-1][3]):   #Cost to be at MVSC consecutive weeks
			tot_cost += 10
			if final:
				print 'MVSV consec cost\t',
		if (schedule_cand[i][1] == schedule_cand[i-1][1]):   #Cost to be long consecutive weeks
			tot_cost += 2
			if final:
				print 'long consec cost\t',
		if (schedule_cand[i-1][0] == schedule_cand[i][0]):  #cost of back to back call
			tot_cost += 2000
			if final:
				print 'back to back call cost\t',
		if (i > 1 and schedule_cand[i][0] == schedule_cand[i-2][0]):	#Cost to be on call 2 times in 3 weeks
			tot_cost += 1000
			if final:
				print '2 in 3 call cost\t',
		if (i > 2 and schedule_cand[i][0] == schedule_cand[i-3][0]):	#Cost to be on call 2 times in 4 weeks
			tot_cost += 10
			if final:
				print '2 in 4 call cost\t',
		if (i > 3 and schedule_cand[i][0] == schedule_cand[i-4][0]):	#Cost to be on call 2 times in 5 weeks
			tot_cost += 5
			if final:
				print '2 in 5 call cost\t',
		if (schedule_cand[i][0] == schedule_cand[i-1][5]):	#Cost to be call following Regina
			tot_cost += 3
			if final:
				print 'call following Regina cost\t',
		if (schedule_cand[i][4] == schedule_cand[i-1][0]):	 #Cost reduction to be on call prior to vacation
			tot_cost -= 5
			if final:
				print 'call before vaca reduction\t',
		if (schedule_cand[i][1] == 2 or schedule_cand[i][2] == 2):  #Cost of Brian to be at SF
			tot_cost += 1
			if final:
				print 'Brian at St.Franny\t',
		tot_cost += len([q for q in range(6) if schedule_cand[i-1][q] == schedule_cand[i][q]]) #increase cost of being consecutive weeks anywhere
	sum_shifts = np.zeros((5,6))
	for i in range(1,7):
		sum_shifts[0,i-1] = (schedule_cand[1:,0]==i).sum()
		sum_shifts[1,i-1] = (schedule_cand[1:,1]==i).sum()
		sum_shifts[2,i-1] = (schedule_cand[1:,2]==i).sum()
		sum_shifts[3,i-1] = (schedule_cand[1:,3]==i).sum()
		sum_shifts[4,i-1] = (schedule_cand[1:,5]==i).sum()
	tot_cost += calc_shifts(sum_shifts)
	return tot_cost

def calc_shifts(a):
	#cost calculation to steer shift distribution
	cost = 0
	call_cost = abs(a[0,0] - 9) + abs(a[0,1] - 9) + abs(a[0,2] - 9) + abs(a[0,3] - 9) + abs(a[0,4] - 8) + abs(a[0,5] - 8)  #9 calls for everyone except Tim and Ryan
	long_cost = sum([max(0, a[1,i] - 18) if i != 3 else max(0, a[1,i] - 26) for i in range(6)])  #less than 18 long shifts for everyone except Mark (26)
	early_cost = sum([max(0, a[2,i] - 13) for i in range(6)]) #less than 13 early shifts for everyone
	early_cost += max(0, (abs(a[2, 0] - a[2, 5])) - 1) #equal early shifts for Jason and Ryan within 1
	early_cost += max(0, (abs(a[2, 2] - a[2, 4])) - 1) #equal early shifts for Dick and Tim within 1
	mvsc_cost = sum([abs(a[3,i] - 13) for i in [0,1,2,5]])  #equal MVSC for MVSC people
	regina_cost = sum([max(0,a[4,i] - 13) for i in [0,4,5]]) #less than 13 weeks Regina for Jason, Tim, Ryan - Brian gets what is left
	regina_cost += sum([abs(x) for x in [min(0,a[4,i] - 8) for i in [0,4,5]]]) #at least 8 weeks Regina for Regina people
	if final:
		print '\n%d\t%d\t%d\t%d\t%d' % (call_cost, long_cost, early_cost, mvsc_cost, regina_cost)
	cost += (100 * call_cost)
	cost += (50 * long_cost)
	cost += (50 * early_cost)
	cost += (50 * mvsc_cost)
	cost += (50 * regina_cost)
	return cost

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
			print 'Reheating, Temperature = %.2f\tCost = %d' % (temperature, current_cost)
		if random.random() < reset_frequency:
			schedule_cand = best_schedule.copy()
			current_cost = overall_best_cost
			print 'Reset to best_schedule.  Temperature = %.2f\tCost = %d' % (temperature, overall_best_cost)
	print best_schedule
	print 'Totals:'
	for i in range(1,7):
		print 'Person %d' % i
		print sum(best_schedule[:,:]==i)
	final = True
	cost(best_schedule)
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
