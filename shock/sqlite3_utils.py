import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(levelname)-8s %(asctime)s : %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p',
                    filename='server_4.log',
                    filemode='a+')


def create_table(conn, table_name, fields):
    cursor = conn.cursor()
    cursor.execute(
        'SELECT name FROM sqlite_master WHERE type="table" AND name="{}"'
        .format(table_name)
    )
    result = cursor.fetchall()
    if len(result) != 0:
        logging.warning("[S4] SQLite3 table {} already exists".format(table_name))
        return

    fields_list = ['%s %s' % (field, field_type) for field, field_type in fields.items()]
    fields_str = ", ".join(fields_list)
    statement = 'CREATE TABLE {} ({})'.format(
        table_name,
        fields_str
    )

    cursor.execute(statement)
    logging.info("[S4] SQLite3 table {} created".format(table_name))


def insert_many_delays(conn, delays):
    # delays format: list(tuple(str, str, float))
    c = conn.cursor()
    c.execute('INSERT INTO stats_delay (ip_src, ip_dst, delay, comm) VALUES (?,?,?,?)', delays)
    conn.commit()
    logging.info("[S4] Inserted {} into stats_delay")


def insert_many_rtts(conn, rtts):
    # rtts format: list(tuple(str, str, float))
    c = conn.cursor()
    c.execute('INSERT INTO stats_rtt (ip_src, ip_dst, rtt, comm) VALUES (?,?,?,?)', rtts)
    conn.commit()
    logging.info("[S4] Inserted {} into stats_rtt")
