import click


@click.command()
@click.option('-o', '--addr-s2', required=True, help='ip:port')
def main(addr_s2):
    pass


if __name__ == '__main__':
    main()
