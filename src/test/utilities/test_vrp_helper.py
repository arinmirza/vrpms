from src.utilities.vrp_helper import convert_duration


def test_convert_duration(T: int = 12, n: int = 5):
    duration_old = [[[0 for _ in range(n)] for _ in range(n)] for _ in range(T)]
    duration = convert_duration(n, duration_old)
    assert len(duration) == n
    assert len(duration[0]) == n
    assert len(duration[0][0]) == T
