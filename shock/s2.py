import click


@click.command()
@click.option('-i', '--addr-s1', required=True, help='ip:port')
@click.option('-o', '--addr-s3', required=True, help='ip:port')
def main(addr_s1, addr_s3):
    pass


if __name__ == '__main__':
    main()
