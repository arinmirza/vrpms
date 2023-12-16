import numpy as np

INPUT_NPY_FILE = "../../../data/mapbox/matrix.npy"
OUTPUT_TXT_FILE = "../../../data/mapbox/matrix.txt"

if __name__ == "__main__":
    data = np.load(INPUT_NPY_FILE)
    n, h = data.shape[0], data.shape[2]
    data_repr = ""
    for i in range(n):
        data_i_repr = ""
        for j in range(n):
            data_i_j_repr = ""
            for k in range(h):
                if k > 0:
                    data_i_j_repr += ","
                data_i_j_repr += str(data[i, j, k])
            data_i_j_repr = "[" + data_i_j_repr + "]"
            if j > 0:
                data_i_repr += ","
            data_i_repr += data_i_j_repr
        data_i_repr = "[" + data_i_repr + "]"
        if i > 0:
            data_repr += ","
        data_repr += data_i_repr
    data_repr = "[" + data_repr + "]"
    with open(OUTPUT_TXT_FILE, "w") as text_file:
        text_file.write(data_repr)
