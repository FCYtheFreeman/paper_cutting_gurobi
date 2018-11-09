# -*- coding: utf-8 -*-
#!/usr/bin/env python
######################################
####    Roll paper cutting task   ####
######################################

#### Version    : 7.0
#### Date       : 2 Apr ~ 7 July, 2018
#### Author     : Chang-yang Fu & Xi Liu
#### Optimizeer : Gurobi8.0.0

from gurobipy import *
import numpy as np
np.set_printoptions(threshold=np.inf)
#from cut_paper2 import input_data
import time

time_start=time.time()
#small_sizes, small_amounts, big_size, big_amount, all_small_sizes_num = input_data()

# small_sizes = [0,1100,1200]
# small_amounts = [10,10]
# big_size = 6300
# big_amount = 5

# small_sizes = [0,900,1000,1100,1150,1300,1350,1400,1500,1550,1600,1700,1750,1900,2000,2100,2200]
# small_amounts = [4,4,4,10,22,9,2,2,2,2,4,2,4,2,2,2]
# big_size = 6300
# big_amount = 17

# small_sizes = [0,800,830,850,885,900,950,1000,1050,1100,1150,1200,1250,1300,1350,1400,1700,2050,2100]
# small_amounts = [14,75,5,50,24,4,4,6,14,9,16,108,7,16,14,2,3,5]
# big_size = 6300
# big_amount = 65

# small_sizes = [0,605,665,725,785,787,800,850,885,900,1025,1050,1200,1250,1300,1400,1450,1574,1800,1920]
# small_amounts = [24,151,13,15,81,10,50,48,18,21,13,15,4,4,5,26,10,15,9]
# big_size = 6300
# big_amount = 76

small_sizes = [0,605,665,725,785,787,800,850,885,900,1025,1200,1250,1300,1450,1574,1920]
small_amounts = [24,151,13,15,81,10,50,48,5,21,6,4,4,26,10,9]
big_size = 6300
big_amount = 75 #65

#common_sizes =[850,900,950,1000,1050,1150,1200,1250,1300,1350,1400,1450,1600,1650,1750,1800,1850,1950]
common_sizes =[850,900,1400,1800]
#common_sizes = [800,900]
new_smallsizes = small_sizes + common_sizes

big_weight = 5
time_limit = 15 #单位为分钟

zone= np.zeros(len(new_smallsizes))
plans = []
num=0
len_of_new_smallsizes = len(new_smallsizes)
for i1 in range(0, len_of_new_smallsizes):
    for i2 in range(i1, len_of_new_smallsizes):
        for i3 in range(i2, len_of_new_smallsizes):
            for i4 in range(i3, len_of_new_smallsizes):
                for i5 in range(i4, len_of_new_smallsizes):
                    for i6 in range(i5, len_of_new_smallsizes):
                        for i7 in range(i6, len_of_new_smallsizes):
                            n = 0
                            sum7 = new_smallsizes[i1] + new_smallsizes[i2] + new_smallsizes[i3] + new_smallsizes[i4] + new_smallsizes[i5] + new_smallsizes[i6] + new_smallsizes[i7]
                            if i1 != 0:
                                n = n + 1
                            if i2 != 0:
                                n = n + 1
                            if i3 != 0:
                                n = n + 1
                            if i4 != 0:
                                n = n + 1
                            if i5 != 0:
                                n = n + 1
                            if i6 != 0:
                                n = n + 1
                            if i7 != 0:
                                n = n + 1
                            if 0 <= big_size - sum7 <= 50:
                                zone= np.zeros(len(new_smallsizes))
                                zone[i1] = zone[i1] + 1
                                zone[i2] = zone[i2] + 1
                                zone[i3] = zone[i3] + 1
                                zone[i4] = zone[i4] + 1
                                zone[i5] = zone[i5] + 1
                                zone[i6] = zone[i6] + 1
                                zone[i7] = zone[i7] + 1
                                zone[0] = big_size - sum7
                                plans.append(zone)


A = np.array(plans)
A = A.T
A = A.astype(int)

# # 删掉组合中小卷数超出规定的组合
# count = []
# for i in range(len_of_small_sizes):
#     for j in range(A.shape[1]):
#         if A[i,j] > small_amounts[i]:
#             count.append(j)
# A = np.delete(A,count,axis=1)
B = np.array(small_amounts)
B.shape = (len(small_amounts),1)

try:
    # gurobi解整数非线性规划
    X_NUM = A.shape[1]  # A矩阵列数
    model = Model("cutpaper")
    model.setParam('TimeLimit', time_limit*60) # 设定最长时限，单位为秒
    variables = []
    sols = []
    # 设置变量
    for i in range(X_NUM):
        variables.append(model.addVar(vtype=GRB.INTEGER,lb=0, ub=big_amount, name="X%d"%i))
    # 目标函数
    model.setObjective(sum([variables[i]*variables[i] for i in range(X_NUM)]), GRB.MAXIMIZE)
    # 约束条件
    for i in range(len(small_sizes)-1):
        sum1 = sum(A[i+1][j]*variables[j] for j in range(X_NUM)) == B[i]
        sum2 = sum(variables[i] for i in range(X_NUM)) == big_amount
        model.addConstr(sum1)
        model.addConstr(sum2)
    model.optimize()

    # Status checking
    status = model.Status
    if status == GRB.Status.INF_OR_UNBD or \
       status == GRB.Status.INFEASIBLE  or \
       status == GRB.Status.UNBOUNDED:
        print('无解，请调整规定规格或备用规格后重试。')
        sys.exit(1)

    #生成最佳解向量
    sol = []
    for i in model.getVars():
        val = round(i.X)
        sol.append(val)
    res = np.array(sol)
    res = res.astype(int)

    # 找出最佳解对应的方案和数量
    best_pla = []
    best_plan_num = []
    backup_pla = []
    for i in range(A.shape[1]):
        if res[i] != 0:
            best_pla.append(A[1:len(new_smallsizes), i].T)
            best_plan_num.append(res[i])
            backup_pla.append(A[len(small_sizes):len(new_smallsizes),i].T)
    best_plas = np.array(best_pla)
    best_plan_num = np.array(best_plan_num)
    backup_plas = np.array(backup_pla)
    backup_plas = backup_plas.sum(axis=0) # 每一列相加
    best_plas = best_plas.astype(int)
    best_plan_num = best_plan_num.astype(int)

    #
    best_plans = []
    for x in range(best_plas.shape[0]):
        best_plan = []
        for i in range(len_of_new_smallsizes-1):
            if best_plas[x,i] != 0:
                for j in range(best_plas[x,i]):
                    best_plan.append(new_smallsizes[i+1])
        best_plans.append(best_plan)
        long = sum(best_plans[x])
        print(best_plans[x],'合计长度:',long,'切割大卷数:',best_plan_num[x],'重量:',best_plan_num[x]*big_weight)

    print('排刀总步骤数:',best_plas.shape[0])
    print('切割大卷总数量：',sum(best_plan_num))
    print('货物总重(吨)：',sum(best_plan_num)*big_weight)

    print('备用尺寸使用情况：')
    for i in range(len(common_sizes)):
        print(common_sizes[i],'：',backup_plas[i])
    time_end=time.time()
    print('方案计算时间(秒)：',round(time_end-time_start,2))

except GurobiError as e:
    print('Error code ' + str(e.errno) + ": " + str(e))

except AttributeError:
    print('Encountered an attribute error')
