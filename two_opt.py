#!/usr/bin/env python

#Schedule is Call, Long, Short, MVSC, Vacation, Regina
#1:'Jason', 2:'Brian', 3:'Dick', 4:'Mark', 5:'Tim', 6:'Ryan'

import numpy as np
import itertools
import random
import sys
import math
import logging

def cost(schedule_cand):
    tot_cost = 0
    for i in range(1, len(schedule_cand)):
        if (schedule_cand[i][3] == schedule_cand[i-1][3]):   #Cost to be at MVSC consecutive weeks
            tot_cost += 10
        if (i > 1):
            if (schedule_cand[i][3] == schedule_cand[i-1][3] and schedule_cand[i-1][3] == schedule_cand[i-2][3]):   #Cost to be at MVSC 3 consecutive weeks
                tot_cost += 200
            if (schedule_cand[i][3] == schedule_cand[i-2][3]):  #Cost to be at MVSC 2 out of 3 weeks
                tot_cost += 5
        if (schedule_cand[i][5] == schedule_cand[i-1][5]):   #Cost to be at Regina consecutive weeks
            tot_cost += 2
        if (i > 1):
            if (schedule_cand[i][5] == schedule_cand[i-1][5] and schedule_cand[i-1][5] == schedule_cand[i-2][5]):   #Cost to be at Regina 3 consecutive weeks
                tot_cost += 20
            if (schedule_cand[i][5] == schedule_cand[i-2][5]):  #Cost to be at Regina 2 out of 3 weeks
                tot_cost += 3
            if (i > 6):
                if (sum(schedule_cand[i-6:i,5]==2) == 0):
                    tot_cost += 10
        if (schedule_cand[i][1] == schedule_cand[i-1][1]):   #Cost to be long consecutive weeks
            tot_cost += 2
        if (schedule_cand[i-1][0] == schedule_cand[i][0]):  #cost of back to back call
            tot_cost += 2000
        if (i > 1 and schedule_cand[i][0] == schedule_cand[i-2][0]):    #Cost to be on call 2 times in 3 weeks
            tot_cost += 1000
        if (i > 2 and schedule_cand[i][0] == schedule_cand[i-3][0]):    #Cost to be on call 2 times in 4 weeks
            tot_cost += 25
        if (i > 3 and schedule_cand[i][0] == schedule_cand[i-4][0]):    #Cost to be on call 2 times in 5 weeks
            tot_cost += 5
        if (schedule_cand[i][0] == schedule_cand[i-1][5]):  #Cost to be call following Regina
            tot_cost += 8
        if (schedule_cand[i][4] == schedule_cand[i-1][0]):   #Cost reduction to be on call prior to vacation
            tot_cost -= 5
        if (schedule_cand[i][1] == 2 or schedule_cand[i][2] == 2):  #Cost of Brian to be at SF
            tot_cost += 1
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
    long_cost = sum([max(0, a[1,i] - 13) if i != 3 else max(0, a[1,i] - 26) for i in range(6)])  #less than 18 long shifts for everyone except Mark (26)
    early_cost = sum([max(0, a[2,i] - 13) for i in range(6)]) #less than 13 early shifts for everyone
    early_cost += max(0, (abs(a[2, 0] - a[2, 5])) - 1) #equal early shifts for Jason and Ryan within 1
    early_cost += max(0, (abs(a[2, 2] - a[2, 4])) - 1) #equal early shifts for Dick and Tim within 1
    mvsc_cost = sum([abs(a[3,i] - 13) for i in [0,1,2,5]])  #equal MVSC for MVSC people
    regina_cost = sum([max(0,a[4,i] - 13) for i in [0,4,5]]) #less than 13 weeks Regina for Jason, Tim, Ryan - Brian gets what is left
    regina_cost += sum([abs(x) for x in [min(0,a[4,i] - 8) for i in [0,4,5]]]) #at least 8 weeks Regina for Regina people
    cost += (100 * call_cost)
    cost += (50 * long_cost)
    cost += (50 * early_cost)
    cost += (50 * mvsc_cost)
    cost += (50 * regina_cost)
    return cost

def gen_schedules(schedule_cand, m_filename):       #Generate schedule candidates using simulated annealing
    global master_cand
    master_cand = read_input(m_filename)
    current_cost = cost(schedule_cand)
    flag = True
    while (flag):
        flag = False
        for i in range(1, 52):
            for x in [0, 1, 2, 3]:
                for y in [1, 2, 3, 5]:
                    if (x != y):
                        for j in range(i, 53):
                            if (master_cand[i, x] == 0 and master_cand[i, y] == 0 and master_cand[j, x] == 0 and master_cand[j, y] == 0):  #only swap non-requested slots
                                if (schedule_cand[i, x] == schedule_cand[j, y] and schedule_cand[i, y] == schedule_cand[j, x]):
                                    before_cost = cost(schedule_cand)
                                    schedule_cand = do_swap(i, j, x, y, schedule_cand)
                                    after_cost = cost(schedule_cand)
                                    if (after_cost >= before_cost):
                                        schedule_cand = do_swap(i, j, x, y, schedule_cand)
                                    else:
                                        print 'swapped (i = %d, j = %d, x = %d, y = %d), new cost: %d' % (i, j, x, y, after_cost)
                                        flag = True
    return schedule_cand

def do_swap(i, j, x, y, schedule_cand):
    temp1 = schedule_cand[i, x]
    temp2 = schedule_cand[i, y]
    schedule_cand[i, x] = temp2
    schedule_cand[i, y] = temp1
    schedule_cand[j, x] = temp1
    schedule_cand[j, y] = temp2
    return schedule_cand

def read_input(filename):
    schedule_cand = np.genfromtxt(filename, delimiter=',')
    assert schedule_cand.shape==(53,6)
    return schedule_cand

def save_result(filename, schedule_cand):
    np.savetxt(filename[:-4] + '_2opt.csv', schedule_cand, delimiter=',')
    logging.info('saved schedule to schedules/%s', filename)

def run_schedule(s_filename, savename):
    schedule_cand = read_input(s_filename)
    schedule_cand = gen_schedules(schedule_cand, m_filename)
    save_result(s_filename, schedule_cand)

if __name__ == "__main__":
    try:
        s_filename = sys.argv[1]
        m_filename = sys.argv[2]
    except:
        print'Please supply the name of the input file and output file'
        sys.exit()
    run_schedule(s_filename, m_filename)
