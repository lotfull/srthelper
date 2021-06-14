import collections
import copy
import json
import platform
import pprint
import subprocess
from re import compile as re_compile

providers = {
    'speedtest-nyc1.digitalocean.com': {'region': 'nyc1', 'provider': 'DO'},
    'speedtest-nyc2.digitalocean.com': {'region': 'nyc2', 'provider': 'DO'},
    'speedtest-nyc3.digitalocean.com': {'region': 'nyc3', 'provider': 'DO'},
    'speedtest-ams2.digitalocean.com': {'region': 'ams2', 'provider': 'DO'},
    'speedtest-ams3.digitalocean.com': {'region': 'ams3', 'provider': 'DO'},
    'speedtest-sfo1.digitalocean.com': {'region': 'sfo1', 'provider': 'DO'},
    'speedtest-sfo2.digitalocean.com': {'region': 'sfo2', 'provider': 'DO'},
    'speedtest-sfo3.digitalocean.com': {'region': 'sfo3', 'provider': 'DO'},
    'speedtest-sgp1.digitalocean.com': {'region': 'sgp1', 'provider': 'DO'},
    'speedtest-lon1.digitalocean.com': {'region': 'lon1', 'provider': 'DO'},
    'speedtest-fra1.digitalocean.com': {'region': 'fra1', 'provider': 'DO'},
    'speedtest-tor1.digitalocean.com': {'region': 'tor1', 'provider': 'DO'},
    'speedtest-blr1.digitalocean.com': {'region': 'blr1', 'provider': 'DO'},
    'ec2.eu-north-1.amazonaws.com': {'region': 'eu-north-1', 'provider': 'AWS'},
    'ec2.ap-south-1.amazonaws.com': {'region': 'ap-south-1', 'provider': 'AWS'},
    'ec2.eu-west-3.amazonaws.com': {'region': 'eu-west-3', 'provider': 'AWS'},
    'ec2.eu-west-2.amazonaws.com': {'region': 'eu-west-2', 'provider': 'AWS'},
    'ec2.eu-west-1.amazonaws.com': {'region': 'eu-west-1', 'provider': 'AWS'},
    'ec2.ap-northeast-3.amazonaws.com': {'region': 'ap-northeast-3', 'provider': 'AWS'},
    'ec2.ap-northeast-2.amazonaws.com': {'region': 'ap-northeast-2', 'provider': 'AWS'},
    'ec2.ap-northeast-1.amazonaws.com': {'region': 'ap-northeast-1', 'provider': 'AWS'},
    'ec2.sa-east-1.amazonaws.com': {'region': 'sa-east-1', 'provider': 'AWS'},
    'ec2.ca-central-1.amazonaws.com': {'region': 'ca-central-1', 'provider': 'AWS'},
    'ec2.ap-southeast-1.amazonaws.com': {'region': 'ap-southeast-1', 'provider': 'AWS'},
    'ec2.ap-southeast-2.amazonaws.com': {'region': 'ap-southeast-2', 'provider': 'AWS'},
    'ec2.eu-central-1.amazonaws.com': {'region': 'eu-central-1', 'provider': 'AWS'},
    'ec2.us-east-1.amazonaws.com': {'region': 'us-east-1', 'provider': 'AWS'},
    'ec2.us-east-2.amazonaws.com': {'region': 'us-east-2', 'provider': 'AWS'},
    'ec2.us-west-1.amazonaws.com': {'region': 'us-west-1', 'provider': 'AWS'},
    'ec2.us-west-2.amazonaws.com': {'region': 'us-west-2', 'provider': 'AWS'},
}


def ping(host, tries=1):
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, str(tries), host]
    out = subprocess.run(command, capture_output=True, text=True)
    return out.stdout


def ping_servers(provider='DO', tries=1, output='ping.json'):
    if provider == 'all':
        servers = {host: data for host, data in providers.items()}
    else:
        servers = {host: data for host, data in providers.items() if data['provider'] == provider}

    expression = re_compile('(\d+.\d+)/(\d+.\d+)/(\d+.\d+)/(\d+.\d+) ms')

    for host, data in servers.items():
        ping_result = ping(host, tries=tries)
        print(f'{host}, {ping_result=}')
        ping_ms = float(expression.search(ping_result).group(2))
        data['ping'] = ping_ms

    print("\n\nLowest latency region: ")
    sorted_servers = list(sorted(servers.items(), key=lambda host_data: host_data[1]['ping']))
    for i, (host, data) in enumerate(sorted_servers):
        print(f'{i}) {host}: {data["ping"]} ms')
    with open(output, 'w') as f:
        json.dump(servers, f)

    return sorted_servers


def best_ping_server(src_ping, dst_ping, output=None, sort_by=None, export=None):
    output = output or 'bestping.json'
    sort_by = sort_by or 'ping'
    export = export or False
    with open(src_ping, 'r') as f:
        src_pings = json.load(f)
    with open(dst_ping, 'r') as f:
        dst_pings = json.load(f)

    host_pings = collections.defaultdict(dict)
    servers_common = set(src_pings.keys()).intersection(dst_pings.keys())

    for host in servers_common:
        host_pings[host] = copy.deepcopy(src_pings[host])
        host_pings[host]['dst_ping'] = dst_pings[host]['ping']
        host_pings[host]['total_ping'] = host_pings[host]['ping'] + host_pings[host]['dst_ping']

    sorted_host_pings = sorted(host_pings.items(), key=lambda host_data: host_data[1][sort_by])
    best_host = sorted_host_pings[0]
    pprint.pprint(sorted_host_pings)
    with open(output, 'w') as f:
        json.dump(sorted_host_pings, f)

    if export:
        print(f'--provider={best_host[1]["provider"]} --region={best_host[1]["region"]} --ping={best_host[1]["ping"]} --dst_ping={best_host[1]["dst_ping"]}')

    return best_host
