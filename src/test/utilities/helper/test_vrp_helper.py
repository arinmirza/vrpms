from src.utilities.helper.vrp_helper import complete_solution_to_arrivals

N_TIME_ZONES = 12  # hours = time slices
N = 9


def test_solution_to_arrivals():
    vehicles_start_times = [10, 20]
    solution = [[[0, 1, 2, 0], [0, 3, 4, 0]], [[0, 5, 6, 0], [0, 7, 8, 0]]]
    expected_arrivals = [[[10, 11, 12, 13], [13, 14, 15, 16]], [[20, 21, 22, 23], [23, 24, 25, 26]]]
    duration = []
    for i in range(N):
        duration_src = []
        for j in range(N):
            duration_src_dest = []
            for t in range(N_TIME_ZONES):
                duration_src_dest.append(int(i != j))
            duration_src.append(duration_src_dest)
        duration.append(duration_src)
    arrivals = complete_solution_to_arrivals(vehicles_start_times, solution, duration)
    assert arrivals == expected_arrivals
