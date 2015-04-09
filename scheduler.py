#!/usr/bin/env python

#Schedule is Call, Long, Short, MVSC, Vacation

import numpy as np
import itertools
import random
import sys
import math

def gen_permutations(n, mvsc_list):							#Generate all possible combinations for a week's schedule
	p = itertools.permutations(list(range(1,n+1)))
	return np.array([list(w) for w in p if w[3] in mvsc_list])

def cost(schedule_cand):
	tot_cost = 0
	for i in range(1, len(schedule_cand)):
		if (np.all(schedule_cand[i])):
			if (schedule_cand[i][3] == schedule_cand[i-1][3]):   #Cost to be at MVSC consecutive weeks
				tot_cost += 10
			if (schedule_cand[i][1] == schedule_cand[i-1][1]):   #Cost to be long consecutive weeks
				tot_cost += 5
			if (i > 1 and schedule_cand[i][0] == schedule_cand[i-2][0]):	#Cost to be on call 2 times in 3 weeks
				tot_cost += 3
			if (schedule_cand[i][4] == schedule_cand[i-1][0] or schedule_cand[i][4] == schedule_cand[i-1][2]):	 #Cost reduction to be on call or early prior to vacation
				tot_cost -= 1
			tot_cost += 1
	return tot_cost

def is_schedule_valid(schedule_cand, target_num):			#Check if valid schedule (approx equal number of MVSC, call, and short weeks)
	div_factor = target_num / 53.
	for i in range(1,6):
		if (schedule_cand[1:target_num,0]==i).sum() > math.ceil(11 * div_factor):	#Equal number of call weeks
			#print 'invalid for call'
			return False
		if (schedule_cand[1:target_num,2]==i).sum() > math.ceil(12 * div_factor):	#Equal number of early weeks
			#print 'invalid for early'
			#print schedule_cand
			return False
		if (schedule_cand[1:target_num,3]==i).sum() > math.ceil(18 * div_factor):	#Equal number of MVSC weeks
			#print 'invalid for MVSC'
			return False
	return True

def are_shifts_equal(schedule_cand, target_num):
	sum_shifts = np.zeros((3,5))
	for i in range(1,6):
		sum_shifts[0,i-1] = (schedule_cand[1:target_num,0]==i).sum()
		sum_shifts[1,i-1] = (schedule_cand[1:target_num,2]==i).sum()
		sum_shifts[2,i-1] = (schedule_cand[1:target_num,3]==i).sum()
	for i in range(3):
		b = np.unique(sum_shifts[i,:])
		if (i < 2 and b[-1] - b[0] > 1):  #equal call and early (within 1)
			return False
		if (i == 2 and b[-1] - b[1] > 1):  #equal MVSC (within 1)
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
			#print 'pruned for cost %d' % week_num
			return False
	if (week_num > 7):
		for i in range(1,6):
			if (schedule_cand[week_num-8:week_num,0]==i).sum() < 1:	#at least 1 call every 8 weeks
				#print 'pruned for call %d' % week_num
				return False
			if (schedule_cand[week_num-8:week_num,2]==i).sum() < 1:	#at least 1 early every 8 weeks
				#print 'pruned for early %d' % week_num
				return False
			if i < 3:
				if (schedule_cand[week_num-6:week_num,3]==i).sum() < 1:	#at least 1 mvsc every 6 weeks
					#print 'pruned for mvsc %d' % week_num
					return False
	return True


def gen_schedules(week_num, schedule_cand, target_num):		#Generate schedule candidates using DFS
	global schedules
	global best_cost
	global overall_best_cost
	if (week_num == target_num):
		if (are_shifts_equal(schedule_cand, target_num)):
			cs = cost(schedule_cand)
			if (cs < best_cost and cs < overall_best_cost):
				if (target_num == 53):
					#if (cs < overall_best_cost):
					schedules.append(np.array(schedule_cand))
					overall_best_cost = cs
					best_cost = cs
					print 'best_cost %d' % best_cost
				else:
					temp = cs
					best_cost = target_num + 13
					print 'week %d best_cost %d' % (week_num, cs)
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

if __name__ == "__main__":
	sys.setrecursionlimit(1000)
	global schedules, perm_list, best_cost, overall_best_cost
	overall_best_cost = 9999
	schedules = list()
	perm_list = gen_permutations(5, [1, 2, 3])
	best_cost = 14
	person_dict = {1:'Jason', 2:'Brian', 3:'Dick', 4:'Mark', 5:'Tim'}
	position_dict = {0:'Call', 1:'Long', 2:'Short', 3:'MVSC', 4:'Vacation'}
	schedule_cand = np.zeros((53,5))
	schedule_cand[0] = np.array([1, 4, 5, 3, 2])    #Last week of previous year's schedule
	schedule_cand[1][0] = 4.   #Call for 1st week from previous year's schedule
	vacations = np.array([3,1,4,2,3,3,2,5,3,3,1,2,4,1,5,4,1,0,4,5,2,5,4,1,2,2,4,3,5,2,3,1,5,4,5,1,2,4,5,3,1,2,5,3,0,1,4,3,5,1,4,2])
	schedule_cand[1:,4] = vacations
	schedule_cand[5][0] = 1.
	schedule_cand[21][0] = 4.
	schedule_cand[27][0] = 3.
	schedule_cand[40][0] = 2.
	schedule_cand[48][0] = 5.
	schedule_cand[52][0] = 1.
	print schedule_cand
	print 'Generating schedules'
	gen_schedules(1, schedule_cand, 14)
	print schedules
	print 'final best cost: %d' % cost(schedules[-1])