import sqlite3


def create_table(conn, table_name, fields):
    cursor = conn.cursor()
    cursor.execute(
        'SELECT name FROM sqlite_master WHERE type="table" AND name="{}"'
        .format(table_name)
    )
    result = cursor.fetchall()
    if len(result) != 0:
        print("SQLite3 table {} already exists".format(table_name))
        return

    fields_list = ['%s %s' % (field, field_type) for field, field_type in fields.items()]
    fields_str = ", ".join(fields_list)
    statement = 'CREATE TABLE {} ({})'.format(
        table_name,
        fields_str
    )

    cursor.execute(statement)
    print("SQLite3 table {} created".format(table_name))


def insert_many_delays(conn, delays):
    # delays format: list(tuple(str, str, float))
    conn.executemany('INSERT INTO stats_delay VALUES (?,?,?)', delays)


def insert_many_rtts(conn, rtts):
    # rtts format: list(tuple(str, str, float))
    conn.executemany('INSERT INTO stats_rtt VALUE (?,?,?)', rtts)