import click
import time
from shock.utils import *

DEFAULT_VALUE = int("".join(['1' for i in range(19)])) / (10 ** 9)
DEFAULT_IP = '255.255.255.255'.encode("utf-8")


def send_delay(sock_s2, addr_s2):
    packer = get_packer('!d 21s d 21s d 21s d 21s')

    time_struct = [
        DEFAULT_VALUE,
        DEFAULT_IP,

        DEFAULT_VALUE,
        DEFAULT_IP,

        DEFAULT_VALUE,
        DEFAULT_IP,

        DEFAULT_VALUE,
        DEFAULT_IP,
    ]

    time_struct[0] = time.time()
    time_struct[1] = addr_s2.encode('utf-8')
    pack = packer.pack(*time_struct)
    sock_s2.send(pack)
    print("[S1] Sent timestruct {} to S2".format(time_struct))


def send_rtt(addr_s1, addr_s2, sock_s2):
    packer = get_packer('!d 21s 21s d 21s 21s d 21s 21s d 21s 21s')

    rtt_struct = [
        DEFAULT_VALUE,
        DEFAULT_IP,
        DEFAULT_IP,

        DEFAULT_VALUE,
        DEFAULT_IP,
        DEFAULT_IP,

        DEFAULT_VALUE,
        DEFAULT_IP,
        DEFAULT_IP,

        DEFAULT_VALUE,
        DEFAULT_IP,
        DEFAULT_IP,
    ]

    rtt_start = time.time()
    sock_s2.send("RTT".encode('utf-8'))
    _ = sock_s2.recv(3)
    rtt_end = time.time()

    rtt_struct[0] = rtt_end - rtt_start
    rtt_struct[1] = addr_s1.encode('utf-8')
    rtt_struct[2] = addr_s2.encode('utf-8')

    pack = packer.pack(*rtt_struct)
    sock_s2.send(pack)
    print("[S1] Sent rtt struct {} to S2".format(rtt_struct))


analyze_types = click.Choice(['delay', 'rtt'])


@click.command()
@click.option('-t', '--analyze-type', type=analyze_types, required=True)
@click.option('-i', '--addr-s1', required=True)
@click.option('-o', '--addr-s2', required=True, help='ip:port')
def main(analyze_type, addr_s1, addr_s2):
    sock_s2 = connect_to_addr(addr_s2)
    print("[S1] Connected to S2.")

    # Process
    if analyze_type == 'delay':
        send_delay(sock_s2, addr_s2)
    elif analyze_type == 'rtt':
        send_rtt(addr_s1, addr_s2, sock_s2)


if __name__ == '__main__':
    main()
