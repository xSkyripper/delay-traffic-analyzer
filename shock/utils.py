import socket
import struct


BROADCAST = '0.0.0.0'
#LOOPBACK = '127.0.0.1' SCUZE ALEX

def connect_to_addr(addr):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ip, port = addr.strip().split(":")
    sock.connect((ip, int(port)))
    return sock


def create_server(addr):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ip, port = addr.strip().split(":")
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((BROADCAST, int(port)))
    sock.listen(1)
    return sock


def get_packer(fmt):
    return struct.Struct(fmt)
