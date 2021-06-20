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
    dst_latency=None,
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
    stats=None,
    stats_file=None,
    stats_type=None,
    stats_freq=None,
):
    bitrate = ureg(bitrate)
    if not isinstance(bitrate, int):
        bitrate = bitrate.to('baud').m
    rtt = rtt or 150
    mss = mss or 1360
    payload = payload or 1316
    src_port = src_port or 1234
    dst_port = dst_port or 1235

    dst_latency = dst_latency or latency

    def srt_query(srt_port, srt_ip=None, srt_fc=None, srt_rcvbuf=None, lat=None):
        return (
            f'srt://{srt_ip or ""}'
            f':{srt_port}'
            f'?rcvlatency={lat or latency}'
            f'&peerlatency={lat or latency}'
            f'&mss={mss}'
            f'&payloadsize={payload}'
            f'&fc={srt_fc}'
            f'&rcvbuf={srt_rcvbuf}'
            f'&sndbuf={srt_rcvbuf}'
        )

    def calc_fc_buf(srt_rtt, lat):
        if fc and rcvbuf:
            return fc, rcvbuf

        full_latency_sec = (lat + srt_rtt / 2) / 1000
        payload_bytes = math.floor(full_latency_sec * bitrate / 8)
        fc_num_packets = math.floor(payload_bytes / payload)
        if fc_num_packets < 32:
            fc_num_packets = 32
        udphdr_size = 28
        rcvbuf_size = fc_num_packets * (mss - udphdr_size)
        calc_fc, calc_rcvbuf = fc or fc_num_packets, rcvbuf or rcvbuf_size
        print(f'{full_latency_sec=}, {lat=}, {srt_rtt=}, {payload_bytes=}, {bitrate=}, {fc_num_packets=}, {payload=}, {udphdr_size=}, {rcvbuf_size=}, {mss=}, {calc_fc=}, {calc_rcvbuf=}')
        return calc_fc, calc_rcvbuf

    if mode == 'direct':
        fc, rcvbuf = calc_fc_buf(rtt, latency)
        srt_config = srt_query(src_port, src_ip, fc, rcvbuf)
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
    name = name or f'{mode}-{ip or provider}-{region or ""}-{src_port}-{dst_port}'

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

    src_fc, src_rcvbuf = calc_fc_buf(src_ping, latency)
    dst_fc, dst_rcvbuf = calc_fc_buf(dst_ping, dst_latency)

    src_srturl = srt_query(src_port, instance_data['ip'], src_fc, src_rcvbuf)
    dst_srturl = srt_query(dst_port, instance_data['ip'], dst_fc, dst_rcvbuf, lat=dst_latency)

    forwarder_src_srturl = srt_query(src_port, srt_fc=src_fc, srt_rcvbuf=src_rcvbuf)
    forwarder_dst_srturl = srt_query(dst_port, srt_fc=dst_fc, srt_rcvbuf=dst_rcvbuf, lat=dst_latency)

    stats_params = f'-statsout {stats_file} -pf {stats_type} -s {stats_freq}' if stats else ''
    docker_mount = '-v $(pwd):$(pwd) -w $(pwd)' if stats else ''

    forwarder_config = f'srt-live-transmit {stats_params} "{forwarder_src_srturl}" "{forwarder_dst_srturl}"'
    forwarder_config_run = f"docker run -d --name={name} --net=host {docker_mount} --restart=unless-stopped fenestron/srt:latest {forwarder_config}"
    forwarder_config_stop = f"docker stop {name} && docker rm {name}"

    config = dict(
        name=name,
        src_srturl=src_srturl,
        dst_srturl=dst_srturl,
        forwarder_config=forwarder_config,
        forwarder_config_run=forwarder_config_run,
        forwarder_config_stop=forwarder_config_stop,
        **instance_data,
    )
    with open(output, 'w') as f:
        json.dump(config, f, indent=2)
    pprint.pprint(config)


COMMANDS = ['run', 'stop', 'test', 'install', 'list']


def forwarder(config_json, mode, clear):
    with open(config_json, 'r') as f:
        config = json.load(f)

    with Connection(host=config['ip'], user=config['user']) as c:
        if clear:
            clear_result = c.run('docker stop $(docker ps -aq) ; docker rm $(docker ps -aq) && rm -rf stats.csv')
            print(f'{clear_result = }')
        if mode == 'run':
            command = config['forwarder_config_run']
        elif mode == 'stop':
            command = config['forwarder_config_stop']
        elif mode == 'test':
            command = 'pwd'
        elif mode == 'install':
            command = 'apt install snap -y && snap install docker'
        elif mode == 'list':
            command = 'docker ps -a'
        command_result = c.run(command)
        print(f'{command = }\n{command_result.stdout = }')
