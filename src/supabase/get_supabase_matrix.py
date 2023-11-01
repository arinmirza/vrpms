import numpy as np
#import os
#CURRENT_PATH = os.getcwd()
def get_data():

    # this method will be called from control.py, thus "/supabase" folder is added to the CURRENT_PATH
    duration_matrix = np.load(file ="dataset_matrix.npy", allow_pickle=True)

    return list (duration_matrix)


get_data()
