import rrdb
import sys
from time import time
from io import StringIO
from argparse import Namespace

_time = lambda: round(time())

def test_init():
    rrdb.drop() # drop all rrdb related tables
    rrdb.init() # recreate tables and add slots
    res = rrdb.sql_query("SELECT name FROM sqlite_master WHERE name in (?,?,?)", 'rrdb_master', 'rrdb_minutes', 'rrdb_hours')
    assert len(res) == 3

def test_save():
    rrdb.save(Namespace(epoch=12343, value=20.5))
    rrdb.save(Namespace(epoch=12344, value=10.5))
    rrdb.save(Namespace(epoch=_time(), value=3.5))
    res = rrdb.sql_query("SELECT * FROM rrdb_minutes WHERE value IS NOT NULL")
    assert res[0] == (1, 12343, 20.5)
    assert res[1] == (2, 12344, 10.5)
    assert res[2][2] == 3.5
    assert res[2][1] > 0

def test_query():
    _stdout = sys.stdout # a nice hack to redirect stdout to a variable!
    temp_buffer = StringIO()
    sys.stdout = temp_buffer
    rrdb.query(Namespace(query_type="minutes"))
    sys.stdout = _stdout
    stats_line = temp_buffer.getvalue().split('\n')[-2]
    assert stats_line == 'minutes: min: 3.5, avg: 11.5, max: 20.5'

def test_save_bulk():
    rrdb.drop()
    rrdb.init()
    rrdb.save(Namespace(epoch=_time(), value=3.0))
    for _ in range (59):
        rrdb.save(Namespace(epoch=_time(), value=3.2))
    minutes = rrdb.sql_query("SELECT * FROM rrdb_minutes")
    assert len(minutes) == 60
    minute_values = [i[2] for i in minutes]
    assert minute_values[0] == 3.0
    rrdb.save(Namespace(epoch=_time(), value=3.1))
    minutes = rrdb.sql_query("SELECT * FROM rrdb_minutes")
    assert len(minutes) == 60
    minute_values = [i[2] for i in minutes]
    assert minute_values[0] == 3.1
    first_hour = rrdb.sql_query("SELECT value FROM rrdb_hours")[0][0]
    assert first_hour == 3.0
    for _ in range(24):
        for _ in range(60):
            rrdb.save(Namespace(epoch=_time(), value=9.2))
    hour_values = rrdb.sql_query("SELECT value FROM rrdb_hours")
    assert hour_values[0][0] == 9.2
