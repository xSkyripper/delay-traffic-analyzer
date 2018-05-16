import click


@click.command()
@click.option('-i', '--addr-s3', required=True, help='ip:port')
def main(addr_s3):
    pass


if __name__ == '__main__':
    main()
