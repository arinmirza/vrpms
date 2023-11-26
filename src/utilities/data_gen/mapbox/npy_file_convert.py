import numpy as np


def run(n: int = 5):
    input_npy_file = f"../../../../data/mapbox/matrix_{n}.npy"
    output_txt_file = f"../../../../data/mapbox/matrix_{n}.txt"
    data = np.load(input_npy_file)
    n, h = data.shape[0], data.shape[2]
    print(f"n = {n} , h = {h}")
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
    with open(output_txt_file, "w") as text_file:
        text_file.write(data_repr)


if __name__ == "__main__":
    run()
