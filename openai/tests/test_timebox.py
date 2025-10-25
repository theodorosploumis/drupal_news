from utils.timebox import get_time_window


def test_time_window_duration():
    window = get_time_window(7, "Europe/Athens")
    delta = window.end - window.start
    assert abs(delta.total_seconds() - 7 * 24 * 3600) < 1800  # allow DST adjustments
