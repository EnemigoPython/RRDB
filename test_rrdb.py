import rrdb
from argparse import Namespace

def test_init():
    rrdb.drop() # drop all rrdb related tables
    rrdb.init() # recreate tables and add slots
    res = rrdb.sql_query("SELECT name FROM sqlite_master WHERE name in (?,?,?)", 'rrdb_master', 'rrdb_minutes', 'rrdb_hours')
    assert len(res) == 3

def test_save():
    rrdb.save(Namespace(epoch=12343, value=20.5))
    rrdb.save(Namespace(epoch=12344, value=10.2))
    rrdb.save(Namespace(epoch=12344, value=3.7))
    res = rrdb.sql_query("SELECT * FROM rrdb_minutes WHERE value IS NOT NULL")
    assert res[0] == (1, 12343, 20.5)
    assert res[1] == (2, 12344, 10.2)
    assert res[2][2] == 3.7
    assert res[2][1] > 0
