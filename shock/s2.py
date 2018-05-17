import click
import time
from shock.utils import *


def send_delay(sock_s1, sock_s3, addr_s2):
    packer = get_packer('!d 21s d 21s d 21s d 21s')

    pack = sock_s1.recv(packer.size)
    time_struct = packer.unpack(pack)
    print("[S2] Received timestruct {} from S1".format(time_struct))

    time_struct = list(time_struct)
    time_struct[2] = time.time()
    time_struct[3] = addr_s2.encode('utf-8')
    pack = packer.pack(*time_struct)
    sock_s3.send(pack)
    print("[S2] Sent timestruct {} to S3".format(time_struct))


def send_rtt(sock_s1, sock_s3, addr_s2, addr_s3):
    packer = get_packer('!d 21s 21s d 21s 21s d 21s 21s')

    _ = sock_s1.recv(3)
    sock_s1.send("RTT".encode('utf-8'))
    pack = sock_s1.recv(packer.size)
    rtt_struct = list(packer.unpack(pack))
    print("[S2] Received rtt struct {} from S1".format(rtt_struct))

    rtt_start = time.time()
    sock_s3.send("RTT".encode('utf-8'))
    _ = sock_s3.recv(3)
    rtt_end = time.time()

    rtt_struct[3] = rtt_end - rtt_start
    rtt_struct[4] = addr_s2.encode('utf-8')
    rtt_struct[5] = addr_s3.encode('utf-8')

    pack = packer.pack(*rtt_struct)
    sock_s3.send(pack)
    print("[S2] Sent rtt struct {} to S3".format(rtt_struct))


analyze_types = click.Choice(['delay', 'rtt'])


@click.command()
@click.option('-t', '--analyze-type', type=analyze_types, required=True)
@click.option('-i', '--addr-s2', required=True, help='S2 ip:port')
@click.option('-o', '--addr-s3', required=True, help='S3 ip:port')
def main(analyze_type, addr_s2, addr_s3):
    server = create_server(addr_s2)
    print("[S2] Serving at {}".format(addr_s2))
    sock_s1, addr_s1 = server.accept()
    print("[S2] S1 connected.")

    sock_s3 = connect_to_addr(addr_s3)
    print("[S2] Connected to S3.")

    # Process
    if analyze_type == 'delay':
        send_delay(sock_s1, sock_s3, addr_s2)
    elif analyze_type == 'rtt':
        send_rtt(sock_s1, sock_s3, addr_s2, addr_s3)


if __name__ == '__main__':
    main()
