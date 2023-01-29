import os
import sqlite3
from time import time
from dotenv import load_dotenv
from argparse import ArgumentParser

def sql_query(text: str, *params):
    """A generic function to execute a SQL query on the SQLite DB in scope"""
    con = sqlite3.connect(os.getenv('DB_PATH'))
    with con:
        res = list(con.execute(text, params))
    con.close()
    return res

def init(*_):
    """Constructs an empty RRDB"""
    assert not sql_query("""
    SELECT name FROM sqlite_master WHERE type='table' AND name IN ('rrdb_master','rrdb_minutes','rrdb_hours')
    """), "Tables already initialised"
    sql_query("CREATE TABLE rrdb_master(name,current,length)")
    print("Created rrdb_master table")
    for rrdb in ('minutes', 60), ('hours', 24):
        sql_query(f"CREATE TABLE rrdb_{rrdb[0]}(slot,epoch,value)")
        sql_query(f"INSERT INTO 'rrdb_master' (name,current,length) VALUES ('{rrdb[0]}',1,{rrdb[1]})")
        print(f"Created rrdb_{rrdb[0]} table")
        for slot in range(1, rrdb[1] + 1):
            sql_query(f"INSERT INTO 'rrdb_{rrdb[0]}' (slot,epoch,value) VALUES ({slot},0,NULL)")
        print('Table populated')

def drop(*_):
    """Destroys any existing RRDB"""
    sql_query('DROP TABLE IF EXISTS rrdb_master')
    sql_query('DROP TABLE IF EXISTS rrdb_minutes')
    sql_query('DROP TABLE IF EXISTS rrdb_hours')
    print('RRDB tables dropped')

def _save_hour():
    current_hours, max_hours = sql_query("SELECT current,length FROM rrdb_master WHERE name='hours'")[0]
    min_value, min_epoch = min(sql_query("SELECT value,epoch FROM rrdb_minutes"), key=lambda x: x[0])
    sql_query("UPDATE rrdb_hours SET value=?, epoch=? WHERE slot=?", min_value, min_epoch, current_hours)
    if current_hours == max_hours:
        sql_query("UPDATE rrdb_master SET current=1 WHERE name='hours'")
    else:
        sql_query("UPDATE rrdb_master SET current=? WHERE name='minutes'", current_hours + 1)

def save(namespace):
    """Saves an epoch timestamp and a float value to the RRDB"""
    epoch, value = namespace.epoch, namespace.value
    assert epoch > 0, 'Invalid epoch value'
    current_minutes, max_minutes = sql_query("SELECT current,length FROM rrdb_master WHERE name='minutes'")[0]
    sql_query("UPDATE rrdb_minutes SET value=?, epoch=? WHERE slot=?", value, epoch, current_minutes)
    sql_query("UPDATE rrdb_master SET current=? WHERE name='minutes'", current_minutes)
    if current_minutes == max_minutes:
        _save_hour()
        sql_query("UPDATE rrdb_master SET current=1 WHERE name='minutes'")
    else:
        sql_query("UPDATE rrdb_master SET current=? WHERE name='minutes'", current_minutes + 1)

def query(namespace):
    """Returns data from the minute or hour table, including a metadata summary"""
    query_type = namespace.query_type
    table = f'rrdb_{query_type}'
    entries = sql_query(f"SELECT epoch,value FROM {table}")
    for entry in entries:
        print(f"{entry[0]}, {entry[1] or 'NULL'}")
    values = [i[1] for i in entries if i[1] is not None]
    if not len(values):
        return
    avg = lambda x: sum(x) / len(x)
    print(f'{query_type}: min: {min(values)}, avg: {avg(values)}, max: {max(values)}')
    

def main():
    load_dotenv()
    con = sqlite3.connect(os.getenv('DB_PATH'))
    parser = ArgumentParser(prog='RRDB')
    subparsers = parser.add_subparsers(dest='cmd {init,save,query}')
    subparsers.required = True

    parser_init = subparsers.add_parser('init')
    parser_init.set_defaults(func=init)
    parser_init = subparsers.add_parser('drop')
    parser_init.set_defaults(func=drop)
    parser_save = subparsers.add_parser('save')
    parser_save.add_argument('epoch', nargs='?', default=round(time()), type=int)
    parser_save.add_argument('value', type=float)
    parser_save.set_defaults(func=save)
    parser_query = subparsers.add_parser('query')
    parser_query.add_argument('query_type', choices=['minutes', 'hours'])
    parser_query.set_defaults(func=query)

    args = parser.parse_args()
    args.func(args)
    con.close()


if __name__ == '__main__':
    main()
