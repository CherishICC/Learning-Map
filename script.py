import numpy as np
import pandas as pd
import random
import sys
import json
import matplotlib.pyplot as plt

# The PolyLine class has the following properties :
# hd - multi-dimensional array to store the points of the high-dimension space
# status - int variable to check if the polyline is fixed(1) or floating(0)
# ld - an array containing the low-dimension mapping of the polyline

class PolyLine:
    def __init__(self, hd, status, ld, resource_id, data_type):
        self.hd = [[hd[i][j] for j in range(len(hd[i]))] for i in range(len(hd))]
        self.status = status
        if status == 1:
            self.ld = ld
        self.resource_name = resource_id
        self.type = data_type

K = 100  # No. of iterations

f = open('JSON_files/' + sys.argv[1])
data = json.load(f)
# initialise_array return a null multi-dimensional array

def initialise_array():
    polyline_hd = []

    for i in range(total_topics):
        point1 = []
        point1.append(i)
        point1.append(0)
        polyline_hd.append(point1)
    return polyline_hd

# Function to draw a scatter plot

def draw_plot(x, y, n):
    plt.figure(figsize=(8, 8))
    plt.scatter(x,y)
    for j, txt in enumerate(n):
        plt.annotate(txt, (x[j], y[j]))
    plt.show()

# This function calculates the stress of the whole mapping. The arguments are the hd list and ld list of 
# the complete mapping. Stress is calculated as the square root of the sum of squared differences 
# between high-dimension distance and the low-dimension distance divided by the sum of square of 
# high-dimension distances. The distances are calculated using L2 norm.

def stress(hd_list, ld_list):
    sum_of_diff = 0
    ld_sum = 0
    hd_sum = 0
    for i in range(len(hd_list)):
        for j in range(i,len(hd_list)):
            hd_dist = 0
            ld_dist = 0
            point1 = np.array(ld_list[i])
            point2 = np.array(ld_list[j])
            ld_dist = np.linalg.norm(point1 - point2)
            for k in range(len(hd_list[i])):
                point1 = np.array(hd_list[i][k])
                point2 = np.array(hd_list[j][k])
                hd_dist += np.linalg.norm(point1 - point2)
            sum_of_diff += np.square(hd_dist - ld_dist)
            hd_sum += np.square(hd_dist)
    stress = np.sqrt(sum_of_diff/hd_sum)
    return stress

# The mapping function uses the global list - polylines to create a mapping in the low-dimension space. 
# Initally all floating polylines are mapped on the x=y line using the ratio of their distance from the 
# starting polyline to distance from all fixed polylines. Next the mapping is perturbed K times. 
# In each perturbation, a random delta is added to each point of the original mapping five times and 
# the stess is calculated. The set of deltas that show the most decrease in stress are added to the original mapping.
# The loop stops when either the mapping perturbs k times or the difference in the original stress and 
# the new stress is less than a fixed epsilon value.

def mapping():

    hd_list = []
    ld_list = []
    status_list = []
    fixed_hd = []
    for polyline in polylines:
        if polyline.status == 1:
            fixed_hd.append(polyline.hd)
    
    # Initial mapping
    x = []
    y = []
    n = []
    index = 0
    for polyline in polylines:
        dist = []
        dist_sum = 0
        if polyline.status == 0:
            for hd in fixed_hd:
                hd_dist = 0
                for i in range(len(hd)):
                    point1 = np.array(hd[i])
                    point2 = np.array(polyline.hd[i])
                    hd_dist += np.linalg.norm(point1 - point2)
                dist.append(hd_dist)
                dist_sum += hd_dist
            polyline.ld = [(dist[0]/dist_sum), (dist[0]/dist_sum)]
        hd_list.append(polyline.hd)
        ld_list.append(polyline.ld)
        status_list.append(polyline.status)

        x.append(polyline.ld[0])
        y.append(polyline.ld[1])
        n.append(index)
        index += 1
        
    # draw_plot(x,y,n)                                                    # Plotting the initial mapping

    # The below code perturbs the mapping K times
    old_stress = stress(hd_list, ld_list)
    new_ld_list = ld_list
    least_stress_ld_list = ld_list
    list_len = len(polylines)
    i = 0
    while i<K:
        flag = 1
        i = i+1
        original_stress = old_stress
        for l in range(5):                                              # Fixed value '5' is used
            for j in range(list_len):
                if(status_list[j] == 0):
                    dx = (random.randrange(-10, 10, 1))/100
                    dy = (random.randrange(-10, 10, 1))/100
                    new_ld_list[j][0] += dx
                    new_ld_list[j][1] += dy
                    if new_ld_list[j][0] < 0:
                        new_ld_list[j][0] = 0
                    if new_ld_list[j][1] < 0:
                        new_ld_list[j][1] = 0
                    if new_ld_list[j][0] > 1:
                        new_ld_list[j][0] = 1
                    if new_ld_list[j][1] > 1:
                        new_ld_list[j][1] = 1

            new_stress = stress(hd_list, new_ld_list)
            if new_stress < old_stress:
                # print(i,l, new_stress)
                least_stress_ld_list = new_ld_list
                old_stress = new_stress
            else:
                new_ld_list = least_stress_ld_list
        
        if((original_stress - old_stress <= 0.00005)):                  # Fixed epsilon value 0.00005 is used
            x = []
            y = []
            n = []
            for j in range(list_len):
                x.append(least_stress_ld_list[j][0])
                y.append(least_stress_ld_list[j][1])
                n.append(j)
            draw_plot(x,y,n)                                            # Plotting the final mapping
            break

    index = 0
    for polyline in polylines:
        polyline.ld = least_stress_ld_list[index]
        rounded_ld = []
        rounded_ld.append(round(polyline.ld[0], 2))
        rounded_ld.append(round(polyline.ld[1], 2))
        print(index, rounded_ld)
        index += 1

    with open('JSON_files/' + sys.argv[2], 'w') as f:
        json.dump([polyline.__dict__ for polyline in polylines], f)


# The add_point function is used to add a new polyline to the existing mapping. 
# The algorithm initialises the mapping of the new polyline based on the average of the ld of the 'k' closest 
# polylines. The new mapping is then perturbed in the below function 'adjust'

def add_point(polyline, flag):                      # Takes polyline object as argument
    distances = []
    line1 = np.array(polyline.hd)
    index=0
    for pl in polylines:
        l = []
        line2 = np.array(pl.hd)
        hd_dist = 0
        for i in range(len(line1)):
            point1 = np.array(line1[i])
            point2 = np.array(line2[i])
            hd_dist += np.linalg.norm(point1 - point2)
        l.append(hd_dist)
        l.append(index)
        index = index+1
        distances.append(l)
    distances.sort()
    closer_pl_ld = []
    n = 5
    for i in range(n):
        closer_pl_ld.append(polylines[distances[i][1]].ld)
    xsum = 0
    ysum = 0
    for p in closer_pl_ld:
        xsum = xsum + p[0]
        ysum = ysum + p[1]
    polyline.ld = [(xsum)/len(closer_pl_ld), (ysum)/len(closer_pl_ld)]    
    adjust(polyline, flag)
    return polyline.ld

def adjust(polyline, flag):
    polylines.append(polyline)
    hd_list = []
    ld_list = []
    i = 0
    index = 0
    for pl in polylines:
        hd_list.append(pl.hd)
        ld_list.append(pl.ld)
        if(polyline.hd == pl.hd and polyline.ld == pl.ld):
            index = i
        i += 1
    old_stress = stress(hd_list, ld_list)
    
    new_ld_list = ld_list
    least_stress_ld_list = ld_list
    for i in range(K):
        dx = (random.randrange(-5, 5, 1))/100
        dy = (random.randrange(-5, 5, 1))/100
        ld_list[index][0] = ld_list[index][0] + dx
        ld_list[index][0] = ld_list[index][1] + dy
        if ld_list[index][0] < 0:
            ld_list[index][0] = 0
        if ld_list[index][1] < 0:
            ld_list[index][1] = 0
        if ld_list[index][0] > 1:
            ld_list[index][0] = 1
        if ld_list[index][1] > 1:
            ld_list[index][1] = 1
        new_ld_list[index] = [ld_list[index][0],  ld_list[index][1]]
        new_stress = stress(hd_list, new_ld_list)
        if new_stress < old_stress and flag == 1:
            least_stress_ld_list = new_ld_list
            x = []
            y = []
            n = []
            for j in range(len(polylines)):
                x.append(least_stress_ld_list[j][0])
                y.append(least_stress_ld_list[j][1])
                n.append(j)
            draw_plot(x,y,n)
    
    polyline.ld = least_stress_ld_list[index]

def pathway(k):
    l = len(polylines)
    polylines_list = polylines
    polylines_list.sort(key=lambda x: x.ld)
    ld_list = []
    index = 1
    while index < l:
        ld_list.append(polylines_list[index-1].ld)
        line1 = np.array(polylines_list[index-1].hd)
        line2 = np.array(polylines_list[index].hd)
        hd_dist = 0
        for i in range(len(line1)):
            point1 = np.array(line1[i])
            point2 = np.array(line2[i])
            hd_dist += np.linalg.norm(point1 - point2)
        j = 1
        while j<k:
            hd = polylines_list[index-1].hd
            for i in range(len(hd)):
                hd[i][1] = hd[i][1] + (j * (hd_dist/k))
            pl = PolyLine(hd, 0, [0,0])
            ld_point = add_point(pl, 0)
            ld_list.append(ld_point)
            polylines.pop()
            j += 1
        index += 1
    ld_list.append(polylines_list[index-1].ld)

    x = []
    y = []
    n = []
    for i in range(len(ld_list)):
        x.append(ld_list[i][0])
        y.append(ld_list[i][1])
        n.append(i)
    plt.scatter(x,y)
    for j, txt in enumerate(n):
        if(txt%k == 0):
            plt.annotate(txt, (x[j], y[j]))
    plt.plot(x,y)

# The code below converts the input data into polyline objects and stores in a global list

total_topics = len(data["topics"])
polylines = []
data_id = ""
data_type = ""

total_polylines = len(data["resources"])            # Reading the total number of polylines
for i in range(total_polylines):
    polyline_hd = initialise_array()
    temp_str = str(i)
    resource_length = len(data["resources"][i][temp_str]["resource_polyline"])
    for j in range(resource_length):
        polyline_hd[data["resources"][i][temp_str]["resource_polyline"][j]["x"]][1] = data["resources"][i][temp_str]["resource_polyline"][j]["y"]
    polylines.append(PolyLine(polyline_hd, 0, [0,0], data_id, data_type))


# Code to plot 4 random polylines

# temp_list = []
# X = []
# Y = []
# for i in range(4):
#     x = []
#     y = []
#     n = []
#     temp = random.randrange(0,len(polylines)-1)
#     temp_list.append(polylines[temp])
#     for j in range(len(temp_list[i].hd)):
#         x.append(temp_list[i].hd[j][0])
#         y.append(temp_list[i].hd[j][1])
#     X.append(x)
#     Y.append(y)
# plt.figure(figsize=(8, 8))
# plt.scatter(X[0],Y[0],s=10,c='red')
# plt.plot(X[0],Y[0],color="red")
# plt.scatter(X[1],Y[1],s=10,c='blue')
# plt.plot(X[1],Y[1],color="blue")
# plt.scatter(X[2],Y[2],s=10,c='yellow')
# plt.plot(X[2],Y[2],color="yellow")
# plt.scatter(X[3],Y[3],s=10,c='green')
# plt.plot(X[3],Y[3],color="green")



# Code to determine the starting and ending polylines. This is done by simply calculating the distance of 
# each polyline from the x-axis and assigning the polyline with the lowest distance as the starting polyline 
# and the one with the highest distance as the ending polyline

max_dist = 0
min_index = -1
max_index = -1
min_dist = sys.maxsize
j = 0
for polyline in polylines:
    dist_sum = 0
    for i in range(len(polyline.hd)):
        dist_sum += polyline.hd[i][1]
    if(max_dist < dist_sum):
        max_dist = dist_sum
        max_index = j
    if(min_dist > dist_sum):
        min_dist = dist_sum
        min_index = j
    j += 1
# print(min_index, max_index)


# The statuses and ld's of these polylines are updated
polylines[min_index].status = 1
polylines[min_index].ld = [0,0]
polylines[max_index].status = 1
polylines[max_index].ld = [1,1]

mapping()