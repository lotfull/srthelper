import click

from app import ping as ping_module
from app import config as config_module


@click.group()
def cli():
    pass


@cli.command()
@click.option('-d', '--provider', help='provider to ping servers from',
              type=click.Choice(['DO', 'AWS', 'all']), default='DO')
@click.option('-t', '--tries', type=int, help='Number of ping tests to each server', default=1)
@click.option('-o', '--output', type=str, help='Output JSON filepath', default='ping.json')
def ping(provider, tries, output):
    click.echo(f"ping {provider=}, {tries=}")
    click.echo(ping_module.ping_servers(provider, tries))


@cli.command()
@click.argument('src_ping', nargs=1)
@click.argument('dst_ping', nargs=1)
@click.option('-o', '--output', type=str, help='Output JSON filepath', default='bestping.json')
def bestping(src_ping, dst_ping, output):
    click.echo(f"bestping {src_ping=}, {dst_ping=}, {output=}")
    click.echo(ping_module.best_ping_server(src_ping, dst_ping, output))


@cli.command()
@click.argument('mode', nargs=1, type=click.Choice(['direct', 'proxy']))
@click.option('-o', '--output', type=str, help='Output JSON filepath', default='config.json')
@click.option('-b', '--bitrate', type=str, help='Bitrate with bps/kbps/Mbps', required=True)
@click.option('--rtt', type=int, help='Round Trip Time (Ping)')
@click.option('--mss', type=int, help='Max Segment size Bytes', default=1360)
@click.option('--payload', type=int, help='Payload size Bytes', default=1316)
@click.option('--latency', type=int, help='Latency ms', default=300)
@click.option('--fc', type=int, help='Flow Control window size')
@click.option('--rcvbuf', type=int, help='Receive Buffer Size')
@click.option('--src_ip', type=str, help='src_ip if proxy is caller')
@click.option('--src_port', type=str, help='src_port', default=1234)
@click.option('--src_ping', type=int, help='ping from src to proxy server')
@click.option('--dst_ip', type=str, help='dst_ip if proxy is caller')
@click.option('--dst_port', type=str, help='dst_port', default=1235)
@click.option('--dst_ping', type=int, help='ping from dst to proxy server')
@click.option('--provider', type=str, help='proxy server provider')
@click.option('--region', type=str, help='proxy server provider region')
@click.option('--access_token', type=str, help='provider token')
@click.option('--access_key', type=str, help='provider key')
@click.option('--access_secret', type=str, help='provider secret')
@click.option('--cpu_type', type=str, help='DO CPU Type', default='s-2vcpu-2gb-amd')
@click.option('--ip', type=str, help='proxy server ip')
@click.option('--user', type=str, help='proxy server user', default='root')
@click.option('--name', type=str, help='name')
def config(**kwargs):
    click.echo(kwargs)
    config_module.create_config(**kwargs)
