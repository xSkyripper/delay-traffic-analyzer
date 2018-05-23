import click
import time
import logging
from shock.utils import *


logging.basicConfig(level=logging.DEBUG,
                    format='%(levelname)-8s %(asctime)s : %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p',
                    filename='server_3.log',
                    filemode='w+')


def send_delay(sock_s2, sock_s4, addr_s3):
    packer = get_packer('!d 21s d 21s d 21s d 21s')

    pack = sock_s2.recv(packer.size)
    time_struct = packer.unpack(pack)
    logging.info("[S3] Received timestruct {} from S2".format(time_struct))

    time_struct = list(time_struct)
    time_struct[4] = time.time()
    time_struct[5] = addr_s3.encode('utf-8')
    pack = packer.pack(*time_struct)
    sock_s4.send(pack)
    logging.info("[S3] Sent timestruct {} to S4".format(time_struct))


def send_rtt(sock_s2, sock_s4, addr_s3, addr_s4):
    packer = get_packer('!d 21s 21s d 21s 21s d 21s 21s')

    _ = sock_s2.recv(3)
    logging.info("[S3] Received RTT from S2")
    sock_s2.send("RTT".encode('utf-8'))
    logging.info("[S3] Sent RTT to S2")
    pack = sock_s2.recv(packer.size)
    rtt_struct = list(packer.unpack(pack))
    logging.info("[S3] Received RTT struct {} from S2".format(rtt_struct))

    rtt_start = time.time()
    sock_s4.send("RTT".encode('utf-8'))
    logging.info("[S3] Sent RTT to S4")
    _ = sock_s4.recv(3)
    rtt_end = time.time()
    logging.info("[S3] Received RTT from S4")

    rtt_struct[6] = rtt_end - rtt_start
    rtt_struct[7] = addr_s3.encode('utf-8')
    rtt_struct[8] = addr_s4.encode('utf-8')

    pack = packer.pack(*rtt_struct)
    sock_s4.send(pack)
    logging.info("[S3] Sent RTT struct {} to S4".format(rtt_struct))


analyze_types = click.Choice(['delay', 'rtt'])


@click.command()
@click.option('-t', '--analyze-type', type=analyze_types, required=True)
@click.option('-i', '--addr-s3', required=True, help='S3 ip:port')
@click.option('-o', '--addr-s4', required=True, help='S4 ip:port')
def main(analyze_type, addr_s3, addr_s4):
    server = create_server(addr_s3)
    logging.info("[S3] Serving at {} using analyze type {}".format(addr_s3, analyze_type))
    sock_s2, addr_s2 = server.accept()
    logging.info("[S3] S2 connected.")

    sock_s4 = connect_to_addr(addr_s4)
    logging.info("[S3] Connected to S4.")

    # Process
    if analyze_type == 'delay':
        send_delay(sock_s2, sock_s4, addr_s3)
    elif analyze_type == 'rtt':
        send_rtt(sock_s2, sock_s4, addr_s3, addr_s4)


if __name__ == '__main__':
    main()
