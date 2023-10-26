import numpy as np


def get_data():

    duration_matrix = np.load(file ='data/matrix.npy', allow_pickle=True)

    return list (duration_matrix)


get_data()
