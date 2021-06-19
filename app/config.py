import math
from pint import UnitRegistry
import math
import click
from . import do_utils
from . import aws_utils
import json
import pprint
from fabric import Connection

from pint import UnitRegistry

ureg = UnitRegistry()


def check_required_option(option, option_name):
    if option is None:
        print(f'{option_name=}, {option=}')
        raise click.exceptions.BadOptionUsage(option_name, message=f'--{option_name} option required')


def launch_instance(name, provider, region, access_token=None, access_key=None, access_secret=None, cpu_type=None):
    check_required_option(provider, 'provider')
    check_required_option(region, 'region')
    if provider == 'DO':
        if access_token is None:
            raise click.exceptions.BadOptionUsage('access_token', message=f'--access_token option for DO provider required')
        droplet = do_utils.create_droplet_by_img(
            token=access_token,
            name=name,
            region=region,
            cpu_type=cpu_type
        )
        instance_data = dict(ip=droplet.ip_address, user='root', droplet_id=droplet.id)
    else:
        if access_secret is None or access_key is None:
            raise click.exceptions.BadOptionUsage('access_key', message=f'--access_key and --access_secret options for AWS provider required')
        raise NotImplementedError()
        # instance_data = dict(ip=droplet.ip_address, user='root', droplet_id=droplet.id)

    return instance_data


def create_config(
    mode,
    output,
    bitrate,
    rtt=None,
    mss=None,
    payload=None,
    latency=None,
    fc=None,
    rcvbuf=None,
    src_ip=None,
    src_port=None,
    src_ping=None,
    dst_ip=None,
    dst_port=None,
    dst_ping=None,
    provider_file=None,
    provider=None,
    region=None,
    access_token=None,
    access_key=None,
    access_secret=None,
    cpu_type=None,
    ip=None,
    user=None,
    name=None,
):
    bitrate = ureg(bitrate)
    if not isinstance(bitrate, int):
        bitrate = bitrate.to('baud').m
    rtt = rtt or 150
    mss = mss or 1360
    payload = payload or 1316
    latency = latency or 300
    src_port = src_port or 1234
    dst_port = dst_port or 1235


    def calc_srt(srt_rtt, srt_port, srt_ip=None, srt_fc=None, srt_rcvbuf=None):
        if not srt_fc or not srt_rcvbuf:
            full_latency_sec = (latency + srt_rtt / 2) / 1000
            payload_bytes = math.floor(full_latency_sec * bitrate / 8)
            fc_num_packets = math.floor(payload_bytes / payload)
            udphdr_size = 28
            rcvbuf_size = fc_num_packets * (mss - udphdr_size)
            srt_fc, srt_rcvbuf = srt_fc or fc_num_packets, srt_rcvbuf or rcvbuf_size
            print(f'{full_latency_sec=}, {latency=}, {srt_rtt=}, {payload_bytes=}, {bitrate=}, {fc_num_packets=}, {payload=}, {udphdr_size=}, {rcvbuf_size=}, {mss=}, {srt_fc=}, {srt_rcvbuf=}')

        srt = (
            f'srt://{srt_ip or ""}'
            f':{srt_port}'
            f'?transtype=live'
            f'&rcvlatency={latency}'
            f'&peerlatency={latency}'
            f'&mss={mss}'
            f'&payloadsize={payload}'
            f'&fc={srt_fc}'
            f'&rcvbuf={srt_rcvbuf}'
            f'&sndbuf={srt_rcvbuf}'
        )
        return srt

    if mode == 'direct':
        srt_config = calc_srt(rtt, src_port, src_ip, fc, rcvbuf)
        print(srt_config)
        return srt_config

    if provider_file:
        with open(provider_file, 'r') as f:
            bestping_list = json.load(f)
            bestping = bestping_list[0][1]
            print(f'{bestping=}')
            provider, region, src_ping, dst_ping = bestping['provider'], bestping['region'], bestping['ping'], bestping['dst_ping']

    if ip is None and provider is None:
        raise click.exceptions.UsageError(message=f'Either --ip or --provider_file or (--provider --region --access-*) options required')
    name = name or f'{mode}-{ip or provider}-{region}-{src_port}-{dst_port}'

    check_required_option(src_ping, 'src_ping')
    check_required_option(dst_ping, 'dst_ping')

    if ip:
        instance_data = dict(ip=ip, user=user)
    else:
        instance_data = launch_instance(
            name=name,
            provider=provider,
            region=region,
            access_token=access_token,
            access_key=access_key,
            access_secret=access_secret,
            cpu_type=cpu_type
        )
        with open('instance_data.json', 'w') as f:
            json.dump(instance_data, f)

    srt_for_src = calc_srt(src_ping, src_port, instance_data['ip'], fc, rcvbuf)
    srt_for_dst = calc_srt(dst_ping, dst_port, instance_data['ip'], fc, rcvbuf)
    proxy_config = f'srt-live-transmit srt://:{src_port} srt://:{dst_port}'
    proxy_config_run = f"docker run -d --name={name} --net=host --restart=unless-stopped fenestron/srt:latest {proxy_config}"
    proxy_config_stop = f"docker stop {name} && docker rm {name}"

    config = dict(
        name=name,
        srt_for_src=srt_for_src,
        srt_for_dst=srt_for_dst,
        proxy_config=proxy_config,
        proxy_config_run=proxy_config_run,
        proxy_config_stop=proxy_config_stop,
        **instance_data,
    )
    with open(output, 'w') as f:
        json.dump(config, f)
    pprint.pprint(config)


COMMANDS = ['run', 'stop', 'test', 'install', 'list']


def proxy(config_json, mode, clear):
    with open(config_json, 'r') as f:
        config = json.load(f)

    with Connection(host=config['ip'], user=config['user']) as c:
        if clear:
            clear_result = c.run('docker stop $(docker ps -aq) ; docker rm $(docker ps -aq)')
            print(f'{clear_result = }')
        if mode == 'run':
            command = config['proxy_config_run']
        elif mode == 'stop':
            command = config['proxy_config_stop']
        elif mode == 'test':
            command = 'pwd'
        elif mode == 'install':
            command = 'apt install snap -y && snap install docker'
        elif mode == 'list':
            command = 'docker ps -a'
        command_result = c.run(command)
        print(f'{command = }\n{command_result.stdout = }')
