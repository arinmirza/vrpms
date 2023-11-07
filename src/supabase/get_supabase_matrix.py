import numpy
import numpy as np
#import os
#CURRENT_PATH = os.getcwd()

import os

cur_path = os.path.dirname(__file__)


def get_data():

    # this method will be called from control.py, thus "/supabase" folder is added to the CURRENT_PATH
    duration_matrix = np.load(file =str(cur_path)+"/dataset_matrix.npy", allow_pickle=True)
    get_stats(duration_matrix)
    return list (duration_matrix)

def get_stats(matrix):

    sum_all_pairs = []

    for i in range(0,len(matrix)):
        group = []
        for j in  range(0,len(matrix[i])):
            group.append(sum(matrix[i][j]))

        group = sum(group)
        sum_all_pairs.append(group)

    sap = np.asarray(sum_all_pairs)
    #stdev = numpy.std(a = sum_all_pairs, axis = 0, keepdims=True)
    perc = sap / sap.sum()
    perc = perc * 100
    #perc = np.percentile(sap)
    return False
get_data()
