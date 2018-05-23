import click
import time
import sqlite3
import logging
from shock.utils import *
from shock.sqlite3_utils import *
from pprint import pprint

logging.basicConfig(level=logging.DEBUG,
                    format='%(levelname)-8s %(asctime)s : %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p',
                    filename='server_4.log',
                    filemode='a+')


def send_delay(sqlite3_conn, sock_s3, addr_s4):
    packer = get_packer('!d 21s d 21s d 21s d 21s')

    pack = sock_s3.recv(packer.size)
    time_struct = packer.unpack(pack)
    logging.info("[S4] Received timestamp {} from S3".format(time_struct))

    time_struct = list(time_struct)
    t = time.time()
    time_struct[6] = t
    time_struct[7] = addr_s4.encode('utf-8')
    pprint("[S4] Final timestruct:")
    pprint(time_struct)
    time_struct = [
        val.decode('utf-8').rstrip('\x00') if isinstance(val, bytes) else val
        for val in time_struct
    ]

    delay_s1_s2 = (float(time_struct[2]) - float(time_struct[0])) * 1000
    delay_s1_s3 = (float(time_struct[4]) - float(time_struct[0])) * 1000
    delay_s1_s4 = (float(time_struct[6]) - float(time_struct[0])) * 1000

    insert_many_delays(sqlite3_conn, [time_struct[1], time_struct[3], delay_s1_s2, 'S1 - S2'])
    insert_many_delays(sqlite3_conn, [time_struct[1], time_struct[5], delay_s1_s3, 'S1 - S3'])
    insert_many_delays(sqlite3_conn, [time_struct[1], time_struct[7], delay_s1_s4, 'S1 - S4'])


def send_rtt(sqlite3_conn, sock_s3):
    packer = get_packer('!d 21s 21s d 21s 21s d 21s 21s')

    _ = sock_s3.recv(3)
    logging.info("[s4] Received RTT from S3")
    sock_s3.send("RTT".encode('utf-8'))
    logging.info("[S4] Sent RTT to S3")
    pack = sock_s3.recv(packer.size)
    rtt_struct = packer.unpack(pack)
    logging.info("[S4] Received RTT struct {} from S3\n\n".format(rtt_struct))

    rtt_struct = [
        val.decode('utf-8').rstrip('\x00') if isinstance(val, bytes) else val
        for val in rtt_struct
    ]

    pprint(rtt_struct)
    insert_many_rtts(sqlite3_conn, [rtt_struct[1], rtt_struct[2], float(rtt_struct[0]) * 1000, 'S1-S2'])
    insert_many_rtts(sqlite3_conn, [rtt_struct[4], rtt_struct[5], float(rtt_struct[3]) * 1000, 'S2-S3'])
    insert_many_rtts(sqlite3_conn, [rtt_struct[7], rtt_struct[8], float(rtt_struct[6]) * 1000, 'S3-S4'])


analyze_types = click.Choice(['delay', 'rtt'])


@click.command()
@click.option('-t', '--analyze-type', type=analyze_types, required=True)
@click.option('-i', '--addr-s4', required=True, help='S4 ip:port')
@click.option('-d', '--db-sqlite3', required=True, help='Path of the SQLite3 DB file')
def main(analyze_type, addr_s4, db_sqlite3):
    sqlite3_conn = sqlite3.connect(db_sqlite3)
    logging.info("[S4] Creating stats_delay SQLite table")
    create_table(sqlite3_conn, 'stats_delay',
                 dict(ip_src='text', ip_dst='text', delay='float', comm='text'))
    logging.info("[S4] Creating stats_rtt SQLite table")
    create_table(sqlite3_conn, 'stats_rtt',
                 dict(ip_src='text', ip_dst='text', rtt='float', comm='text'))

    server = create_server(addr_s4)
    logging.info("[S4] Serving at {} using analyze type {}".format(addr_s4, analyze_type))
    sock_s3, addr_s3 = server.accept()
    logging.info("[S4] S3 connected.")

    # Process
    if analyze_type == 'delay':
        send_delay(sqlite3_conn,sock_s3, addr_s4)
    elif analyze_type == 'rtt':
        send_rtt(sqlite3_conn, sock_s3)


if __name__ == '__main__':
    main()
