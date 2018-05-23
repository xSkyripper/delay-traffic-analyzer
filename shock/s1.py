import click
import time
import logging
from shock.utils import *

DEFAULT_VALUE = int("".join(['1' for i in range(19)])) / (10 ** 9)
DEFAULT_IP = '255.255.255.255'.encode("utf-8")
logging.basicConfig(level=logging.DEBUG,
                    format='%(levelname)-8s %(asctime)s : %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p',
                    filename='server_1.log',
                    filemode='w+')


def send_delay(sock_s2, addr_s1):
    packer = get_packer('!d 21s d 21s d 21s d 21s')
    time_struct = [DEFAULT_VALUE, DEFAULT_IP] * 4

    time_struct[0] = time.time()
    time_struct[1] = addr_s1.encode('utf-8')
    pack = packer.pack(*time_struct)
    sock_s2.send(pack)
    logging.info("[S1] Sent timestruct {} to S2".format(time_struct))


def send_rtt(addr_s1, addr_s2, sock_s2):
    packer = get_packer('!d 21s 21s d 21s 21s d 21s 21s')
    rtt_struct = [DEFAULT_VALUE, DEFAULT_IP, DEFAULT_IP] * 3

    rtt_start = time.time()
    sock_s2.send("RTT".encode('utf-8'))
    logging.info("[S1] Sent RTT to S2")
    _ = sock_s2.recv(3)
    rtt_end = time.time()
    logging.info("[S1] Received RTT from S2")

    rtt_struct[0] = rtt_end - rtt_start
    rtt_struct[1] = addr_s1.encode('utf-8')
    rtt_struct[2] = addr_s2.encode('utf-8')

    pack = packer.pack(*rtt_struct)
    sock_s2.send(pack)
    logging.info("[S1] Sent RTT struct {} to S2".format(rtt_struct))


analyze_types = click.Choice(['delay', 'rtt'])


@click.command()
@click.option('-t', '--analyze-type', type=analyze_types, required=True)
@click.option('-i', '--addr-s1', required=True, help='S1 ip:port')
@click.option('-o', '--addr-s2', required=True, help='S2 ip:port')
def main(analyze_type, addr_s1, addr_s2):
    logging.info("[S1] Using analyze type {}".format(analyze_type))
    sock_s2 = connect_to_addr(addr_s2)
    logging.info("[S1] Connected to S2.")

    # Process
    if analyze_type == 'delay':
        send_delay(sock_s2, addr_s1)
    elif analyze_type == 'rtt':
        send_rtt(addr_s1, addr_s2, sock_s2)

    sock_s2.close()
    logging.info("[S1] Closed connection with S2.")


if __name__ == '__main__':
    main()
