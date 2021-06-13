import collections
import json
import platform
import subprocess
from re import compile                as    re_compile

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


def best_ping_server(files, output='bestping.json'):
    pings_jsons = []
    for file in files:
        with open(file, 'r') as f:
            pings_jsons.append(json.load(f))

    pings_total = collections.defaultdict(int)
    servers_common = set(pings_jsons[0].keys())
    for pings_json in pings_jsons:
        servers_common.intersection(pings_json.keys())

    for pings_json in pings_jsons:
        for host, data in pings_json.items():
            if host in servers_common:
                pings_total[host] += data['ping']

    sorted_servers = sorted(pings_total.items(), key=lambda host_data: host_data[1])
    best_server = min(sorted_servers, key=lambda host_data: host_data[1])
    best_host, best_ping = best_server
    best_data = providers[best_host]
    best_data['host'], best_data['ping'] = best_host, best_ping
    print(best_data)
    with open(output, 'w') as f:
        json.dump(best_data, f)

    return best_data