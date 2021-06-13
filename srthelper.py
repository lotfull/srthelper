from app.ping import ping_servers
import click


@click.group()
def cli():
    pass


@cli.command()
@click.option('-d', '--datacenter', help='datacenter to ping servers from', type=click.Choice(['DO', 'AWS', 'all']), default='DO')
@click.option('-t', '--tries', type=int, help='Number of ping tests to each server', default=1)
def ping(datacenter, tries):
    click.echo(f"ping {datacenter=}, {tries=}")
    click.echo(ping_servers(datacenter, tries))


@cli.command()
def bestdc():
    click.echo("bestdc")


@cli.command()
def config():
    click.echo("config")
