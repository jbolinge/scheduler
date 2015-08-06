#!/usr/bin/env python

#Schedule is Call, Long, Short, MVSC, Vacation, Regina

import numpy as np
import itertools
import random
import sys
import math
import logging

def gen_permutations(n, mvsc_list, regina_list):							#Generate all possible combinations for a week's schedule
	p = itertools.permutations(list(range(1,n+1)))
	temp = np.array([list(w) for w in p if w[3] in mvsc_list])
	temp2 = np.array([list(w) for w in temp if w[-1] in regina_list])
	return np.array([list(w) for w in temp2 if w[2] not in regina_list])

def cost(schedule_cand):
	tot_cost = 0
	for i in range(1, len(schedule_cand)):
		if (np.all(schedule_cand[i])):
			if (schedule_cand[i][3] == schedule_cand[i-1][3]):   #Cost to be at MVSC consecutive weeks
				tot_cost += 7
			if (schedule_cand[i][1] == schedule_cand[i-1][1]):   #Cost to be long consecutive weeks
				tot_cost += 4
			if (i > 1 and schedule_cand[i][0] == schedule_cand[i-2][0]):	#Cost to be on call 2 times in 3 weeks
				tot_cost += 8
			if (schedule_cand[i][0] == schedule_cand[i-1][3]):	#Cost to be call following MVSC
				tot_cost += 1
			if (schedule_cand[i][4] == schedule_cand[i-1][0] or schedule_cand[i][4] == schedule_cand[i-1][2] or schedule_cand[i][4] == schedule_cand[i-1][5]):	 #Cost reduction to be on call or early prior to vacation
				tot_cost -= 1
			tot_cost += len([q for q in range(6) if schedule_cand[i-1][q] == schedule_cand[i][q]]) #increase cost of being consecutive weeks anywhere
			tot_cost += 1
	return tot_cost

def is_schedule_valid(schedule_cand, target_num):			#Check if valid schedule (approx equal number of MVSC, call, and short weeks)
	div_factor = target_num / 53.
	for i in range(1,6):
		if (schedule_cand[1:target_num,0]==i).sum() > math.ceil(9 * div_factor):	#Equal number of call weeks
			return False
		if (i > 2 and i < 6):
			if (schedule_cand[1:target_num,2]==i).sum() > math.ceil(18 * div_factor):	#Equal number of early weeks for Dick, Mark and Tim
				return False
		if (schedule_cand[1:target_num,3]==i).sum() > math.ceil(14 * div_factor):	#Equal number of MVSC weeks for Brian, Jason, Dick, and new guy
			return False
		if (i < 3 or i > 5):
			if (schedule_cand[1:target_num,5]==i).sum() > math.ceil(18 * div_factor):  #Equal number of Regina weeks for Brian, Jason, and new guy
				return False
	return True

def are_shifts_equal(schedule_cand, target_num):
	sum_shifts = np.zeros((4,6))
	for i in range(1,7):
		sum_shifts[0,i-1] = (schedule_cand[1:target_num,0]==i).sum()
		sum_shifts[1,i-1] = (schedule_cand[1:target_num,2]==i).sum()
		sum_shifts[2,i-1] = (schedule_cand[1:target_num,3]==i).sum()
		sum_shifts[3,i-1] = (schedule_cand[1:target_num,5]==i).sum()
	for i in range(4):
		b = np.unique(sum_shifts[i,:])
		if (i == 0 and b[-1] - b[0] > 1):  #equal call (within 1)
			#print 'failed for equal call'
			return False
		if (i != 0 and b[-1] - b[1] > 2):  #equal MVSC/early/Regina (within 2)
			#print 'failed for equal mvsc/early/regina'
			return False
	return True

def get_cands(week, schedule_cand):
	cands = list()
	filled = list(itertools.chain.from_iterable(np.nonzero(schedule_cand[week])))
	for perm in perm_list:
		truth_array = (schedule_cand[week]==perm)
		if (np.array([truth_array[f] for f in filled]).all()):
			if (schedule_cand[week-1][4] != perm[0] and schedule_cand[week-1][0] != perm[0]):	#No call following vacation or back to back call
				cands.append(perm)
	return cands

def no_prune(schedule_cand, week_num):
	if (best_cost < 9999):
		cs = cost(schedule_cand)
		if (cs > best_cost or cs > overall_best_cost):
			#print 'failed for cost of %d, week %d' % (cs, week_num)
			return False
	if (week_num > 10):
		for i in range(1,7):
			if (schedule_cand[week_num-10:week_num,0]==i).sum() < 1:	#at least 1 call every 10 weeks
				#print 'failed call'
				return False
			if ((schedule_cand[week_num-6:week_num,2]==i).sum() + (schedule_cand[week_num-6:week_num,5]==i).sum()) < 1:	#at least 1 early or regina every 6 weeks
				#print 'failed regina/early'
				return False
			if i < 3:
				if (schedule_cand[week_num-8:week_num,3]==i).sum() < 1:	#at least 1 mvsc every 8 weeks
					#print 'failed mvsc'
					return False
	#print 'passed prune week %d' % week_num
	return True


def gen_schedules(week_num, schedule_cand, target_num):		#Generate schedule candidates using DFS
	global schedules
	global best_cost
	global overall_best_cost
	if (week_num == target_num):
		if (are_shifts_equal(schedule_cand, target_num)):
			cs = cost(schedule_cand)
			if (cs < best_cost and cs < overall_best_cost):
				#print 'week_num %d, cost %d' % (week_num, cs)
				if (target_num == 53):
					schedules.append(np.array(schedule_cand))
					overall_best_cost = cs
					best_cost = cs
					logging.info('candidate found, cost %d', overall_best_cost)
				else:
					temp = cs
					best_cost = temp + (2 * target_num)
					logging.info('week %d, cost %d', week_num, cs)
					gen_schedules(target_num, schedule_cand, target_num + 13)
					best_cost = temp
		return
	weeks_cand = get_cands(week_num, schedule_cand)
	temp = np.array(schedule_cand[week_num])
	for cand in random.sample(weeks_cand, len(weeks_cand)):
		schedule_cand[week_num] = cand
		if (is_schedule_valid(schedule_cand, target_num) and no_prune(schedule_cand, week_num)):
			gen_schedules(week_num + 1, schedule_cand, target_num)
	schedule_cand[week_num] = temp
	return

def read_input(filename):
	with open(filename, 'r') as f:
		file_data = f.readlines()
	try:
		lines = [[int(s) for s in i.split(',')] for i in file_data]
		assert len(lines) == 15
	except:
		logging.error('error opening schedule file %s',filename)
		print 'file format invalid: all numbers separated by commas'
		print 'line 1 is last week of previous year'
		print 'line 2 is first week call from previous year'
		print 'line 3 is vacation schedule'
		print 'line 4 is 1st person calls'
		print 'line 5 is 1st person early req (-1 if none)'
		print '.....'
		print 'line 14 is 6th person calls'
		print 'line 15 is 6th person early'
	schedule_cand = np.zeros((53,6))
	schedule_cand[0] = np.array(lines[0])
	schedule_cand[1,0] = lines[1][0]
	schedule_cand[1:,4] = np.array(lines[2])
	schedule_cand = set_calls(schedule_cand, 1, lines[3], is_call=True)
	schedule_cand = set_calls(schedule_cand, 2, lines[5], is_call=True)
	schedule_cand = set_calls(schedule_cand, 3, lines[7], is_call=True)
	schedule_cand = set_calls(schedule_cand, 4, lines[9], is_call=True)
	schedule_cand = set_calls(schedule_cand, 5, lines[11], is_call=True)
	schedule_cand = set_calls(schedule_cand, 6, lines[13], is_call=True)
	schedule_cand = set_calls(schedule_cand, 1, lines[4], is_call=False)
	schedule_cand = set_calls(schedule_cand, 2, lines[6], is_call=False)
	schedule_cand = set_calls(schedule_cand, 3, lines[8], is_call=False)
	schedule_cand = set_calls(schedule_cand, 4, lines[10], is_call=False)
	schedule_cand = set_calls(schedule_cand, 5, lines[12], is_call=False)
	schedule_cand = set_calls(schedule_cand, 6, lines[14], is_call=False)
	return schedule_cand

def set_calls(schedule_cand, emp_num, list_weeks, is_call=True):
	if is_call:
		index = 0
	elif (emp_num in regina_list):
		index = 5
	else:
		index = 2
	for i in list_weeks:
		if i != -1:
			schedule_cand[i, index] = emp_num
	return schedule_cand

def save_result(filename):
	np.savetxt('schedules/' + filename, schedules[-1], delimiter=',')
	logging.info('saved schedule to schedules/%s', filename)

def run_schedule(s_filename, savename):
	global schedules, perm_list, best_cost, overall_best_cost, regina_list
	logging.basicConfig(filename='log/' + savename + '.log', format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO, mode='w')
	sys.setrecursionlimit(1000)
	overall_best_cost = 9999
	schedules = list()
	regina_list = [1,2,6]
	perm_list = gen_permutations(6, [1, 2, 3, 6], regina_list)
	best_cost = 25
	schedule_cand = read_input(s_filename)
	logging.info('beginning schedule generation')
	gen_schedules(1, schedule_cand, 14)
	logging.info('finished schedule generation, best cost %d', cost(schedules[-1]))
	save_result(savename)

if __name__ == "__main__":
	try:
		s_filename = sys.argv[1]
		savename = sys.argv[2]
	except:
		print'Please supply the name of the input file and output file'
		sys.exit()
	person_dict = {1:'Jason', 2:'Brian', 3:'Dick', 4:'Mark', 5:'Tim', 6:'New Guy'}
	position_dict = {0:'Call', 1:'Long', 2:'Short', 3:'MVSC', 4:'Vacation', 5:'Regina'}
	run_schedule(s_filename, savename)