import click


@click.command()
@click.option('-i', '--addr-s2', required=True, help='ip:port')
@click.option('-o', '--addr-s4', required=True, help='ip:port')
def main(addr_s2, addr_s4):
    pass


if __name__ == '__main__':
    main()
