from app.ping import ping_servers, best_ping_server
import click


@click.group()
def cli():
    pass


@cli.command()
@click.option('-d', '--provider', help='provider to ping servers from', type=click.Choice(['DO', 'AWS', 'all']), default='DO')
@click.option('-t', '--tries', type=int, help='Number of ping tests to each server', default=1)
@click.option('-o', '--output', type=str, help='Output JSON filepath', default='ping.json')
def ping(provider, tries, output):
    click.echo(f"ping {provider=}, {tries=}")
    click.echo(ping_servers(provider, tries))


@cli.command()
@click.argument('file', nargs=-1)
@click.argument('output', type=str, default='bestping.json')
def bestping(file, output):
    click.echo(f"bestping {file=}, {output=}")
    click.echo(best_ping_server(file, output))


@cli.command()
def config():
    click.echo("config")
