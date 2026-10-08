import datetime
from helpers import parse_session_time, duration_minutes_calculated, package_lookup

def test_60_phut():
    start, end = parse_session_time("08:00", 60)
    assert start == datetime.time(8,0)
    assert end == datetime.time(9,0)

def test_90_phut():
    start, end = parse_session_time("08:00",90)
    assert start == datetime.time(8,0)
    assert end == datetime.time(9,30)

def test_so_phut():
    duration = duration_minutes_calculated(datetime.time(8,0), datetime.time(9,30))
    assert duration == 90

def packaage():
    name, session = package_lookup(3)
    assert name == "Warrior"
    assert session == 100