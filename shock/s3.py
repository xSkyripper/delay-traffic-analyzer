import click
import time
from shock.utils import *


def send_delay(sock_s2, sock_s4, addr_s3):
    packer = get_packer('!d 21s d 21s d 21s d 21s')

    pack = sock_s2.recv(packer.size)
    time_struct = packer.unpack(pack)
    print("[S3] Received timestruct {} from S2".format(time_struct))

    time_struct = list(time_struct)
    time_struct[4] = time.time()
    time_struct[5] = addr_s3.encode('utf-8')
    pack = packer.pack(*time_struct)
    sock_s4.send(pack)
    print("[S3] Sent timestruct {} to S4".format(time_struct))


def send_rtt(sock_s2, sock_s4, addr_s3, addr_s4):
    packer = get_packer('!d 21s 21s d 21s 21s d 21s 21s d 21s 21s')

    _ = sock_s2.recv(3)
    sock_s2.send("RTT".encode('utf-8'))
    pack = sock_s2.recv(packer.size)
    rtt_struct = list(packer.unpack(pack))
    print("[S3] Received rtt struct {} from S2".format(rtt_struct))

    rtt_start = time.time()
    sock_s4.send("RTT".encode('utf-8'))
    _ = sock_s4.recv(3)
    rtt_end = time.time()

    rtt_struct[6] = rtt_end - rtt_start
    rtt_struct[7] = addr_s3.encode('utf-8')
    rtt_struct[8] = addr_s4.encode('utf-8')

    pack = packer.pack(*rtt_struct)
    sock_s4.send(pack)
    print("[S3] Sent rtt struct {} to S4".format(rtt_struct))


analyze_types = click.Choice(['delay', 'rtt'])


@click.command()
@click.option('-t', '--analyze-type', type=analyze_types, required=True)
@click.option('-i', '--addr-s3', required=True)
@click.option('-o', '--addr-s4', required=True, help='ip:port')
def main(analyze_type, addr_s3, addr_s4):
    server = create_server(addr_s3)
    print("[S3] Serving at {}".format(addr_s3))
    sock_s2, addr_s2 = server.accept()
    print("[S3] S2 connected.")

    sock_s4 = connect_to_addr(addr_s4)
    print("[S3] Connected to S4.")

    # Process
    if analyze_type == 'delay':
        send_delay(sock_s2, sock_s4, addr_s3)
    elif analyze_type == 'rtt':
        send_rtt(sock_s2, sock_s4, addr_s3, addr_s4)


if __name__ == '__main__':
    main()
