#!/usr/bin/env python

#Schedule is Call, Long, Short, MVSC, Vacation, Regina
#1:'Jason', 2:'Brian', 3:'Dick', 4:'Mark', 5:'Tim', 6:'Ryan'

import numpy as np
import itertools
import random
import sys
import math
import logging
from cost import cost


def gen_schedules(schedule_cand, m_filename):       #Generate schedule candidates using simulated annealing
    global master_cand, final
    final = False
    master_cand = read_input(m_filename)
    current_cost = cost(schedule_cand)
    #print 'Current cost: %d' % (current_cost)
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
                                        #print 'swapped (i = %d, j = %d, x = %d, y = %d), new cost: %d' % (i, j, x, y, after_cost)
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
    logging.info('saved schedule to %s', filename[:-4] + '_2opt.csv')
    logging.info('finished schedule generation, best cost %d', cost(schedule_cand))

def run_schedule(s_filename, m_filename):
    logging.basicConfig(filename='log/' + s_filename[10:-4] + '_2opt.log', format='%(asctime)s %(message)s', \
        datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO, mode='w')
    schedule_cand = read_input(s_filename)
    schedule_cand = gen_schedules(schedule_cand, m_filename)
    save_result(s_filename, schedule_cand)

if __name__ == "__main__":
    global final
    final = False
    try:
        s_filename = sys.argv[1]
        m_filename = sys.argv[2]
    except:
        print'Please supply the name of the input file and master file'
        sys.exit()
    run_schedule(s_filename, m_filename)
