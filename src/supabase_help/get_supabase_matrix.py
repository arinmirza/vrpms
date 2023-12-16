import numpy
import numpy as np
#import os
#CURRENT_PATH = os.getcwd()

import os

cur_path = os.path.dirname(__file__)


def get_data():

    # this method will be called from control.py, thus "/supabase_help" folder is added to the CURRENT_PATH
    duration_matrix = np.load(file =str(cur_path)+"/dataset_matrix.npy", allow_pickle=True)
    #get_stats(duration_matrix)
    return list (duration_matrix)


get_data()
