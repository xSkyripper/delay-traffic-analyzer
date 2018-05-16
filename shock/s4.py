import click
import time
from shock.utils import *
from pprint import pprint


def send_delay(sock_s3, addr_s4):
    packer = get_packer('!d 21s d 21s d 21s d 21s')

    pack = sock_s3.recv(packer.size)
    time_struct = packer.unpack(pack)
    print("[S4] Received timestamp {} from S3".format(time_struct))

    time_struct = list(time_struct)
    time_struct[6] = time.time()
    time_struct[7] = addr_s4.encode('utf-8')
    pprint("[S4] Final timestruct:")
    pprint(time_struct)


def send_rtt(sock_s3):
    packer = get_packer('!d 21s 21s d 21s 21s d 21s 21s d 21s 21s')

    _ = sock_s3.recv(3)
    sock_s3.send("RTT".encode('utf-8'))
    pack = sock_s3.recv(packer.size)
    rtt_struct = packer.unpack(pack)
    print("[S4] Received rtt struct {} from S3\n\n".format(rtt_struct))
    from pprint import pprint

    pprint(rtt_struct)


analyze_types = click.Choice(['delay', 'rtt'])


@click.command()
@click.option('-t', '--analyze-type', type=analyze_types, required=True)
@click.option('-i', '--addr-s4', required=True)
def main(analyze_type, addr_s4):
    server = create_server(addr_s4)
    print("[S4] Serving at {}".format(addr_s4))
    sock_s3, addr_s3 = server.accept()
    print("[S4] S3 connected.")

    # Process
    if analyze_type == 'delay':
        send_delay(sock_s3, addr_s4)
    elif analyze_type == 'rtt':
        send_rtt(sock_s3)


if __name__ == '__main__':
    main()
